"""
NCS roster scraper.

Fetches 'Who's Coming' pages for configured NCS events, extracts team rosters,
detects changes against the last snapshot, and posts Slack notifications.
"""

import os
import sys
import logging
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone
from typing import List, Dict, Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.config import settings
from app.database import SessionLocal, init_db
from app.models.team import Team
from app.models.player import Player
from app.models.snapshot import Snapshot
from app.models.change import Change, ChangeType
from scraper.slack_notifier import post_slack_notification

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

NCS_WHOS_COMING_URL = "{base}/events/{event_id}/whos-coming"
NCS_ROSTER_URL = "{base}/teams/{team_id}/roster"

# Seed event IDs to monitor — update these as tournaments are announced
SEED_EVENT_IDS: List[str] = os.getenv("NCS_SEED_EVENT_IDS", "").split(",")


def fetch_page(url: str) -> Optional[BeautifulSoup]:
    try:
        resp = requests.get(url, timeout=15, headers={"User-Agent": "NCS-Dash/1.0"})
        resp.raise_for_status()
        return BeautifulSoup(resp.text, "html.parser")
    except Exception as e:
        log.warning("Failed to fetch %s: %s", url, e)
        return None


def parse_whos_coming(event_id: str) -> List[Dict]:
    """Return list of {ncs_id, name, division, city} for Central Texas teams."""
    url = NCS_WHOS_COMING_URL.format(base=settings.ncs_base_url, event_id=event_id)
    soup = fetch_page(url)
    if not soup:
        return []

    teams = []
    for row in soup.select("table.teams-table tbody tr, div.team-entry"):
        try:
            name_el = row.select_one(".team-name, td.name")
            div_el = row.select_one(".division, td.division")
            city_el = row.select_one(".city, td.city")
            link_el = row.select_one("a[href*='/teams/']")

            if not (name_el and link_el):
                continue

            ncs_id = link_el["href"].rstrip("/").split("/")[-2]
            name = name_el.get_text(strip=True)
            division = div_el.get_text(strip=True) if div_el else ""
            city = city_el.get_text(strip=True) if city_el else ""

            if not _is_monitored(division, city):
                continue

            teams.append(
                {
                    "ncs_id": ncs_id,
                    "name": name,
                    "division": division,
                    "city": city,
                    "region": "Central Texas",
                    "roster_url": NCS_ROSTER_URL.format(
                        base=settings.ncs_base_url, team_id=ncs_id
                    ),
                }
            )
        except Exception:
            continue

    log.info("Event %s: found %d monitored teams", event_id, len(teams))
    return teams


def parse_roster(roster_url: str) -> List[Dict]:
    """Return list of {name, number} from a team roster page."""
    soup = fetch_page(roster_url)
    if not soup:
        return []

    players = []
    for row in soup.select("table.roster-table tbody tr, div.player-entry"):
        try:
            name_el = row.select_one(".player-name, td.name")
            num_el = row.select_one(".jersey, td.number")
            if not name_el:
                continue
            players.append(
                {
                    "name": name_el.get_text(strip=True),
                    "number": num_el.get_text(strip=True) if num_el else None,
                }
            )
        except Exception:
            continue

    return players


def _is_monitored(division: str, city: str) -> bool:
    div_match = any(d.lower() in division.lower() for d in settings.divisions_list)
    city_match = any(c.lower() in city.lower() for c in settings.cities_list)
    return div_match and city_match


def upsert_team(db, team_data: Dict) -> Team:
    team = db.query(Team).filter(Team.ncs_id == team_data["ncs_id"]).first()
    if not team:
        team = Team(**team_data)
        db.add(team)
        db.commit()
        db.refresh(team)
        log.info("Registered new team: %s", team.name)
    return team


def get_or_create_player(db, team_id: int, name: str, number: Optional[str]) -> Player:
    player = db.query(Player).filter(Player.team_id == team_id, Player.name == name).first()
    if not player:
        player = Player(team_id=team_id, name=name, number=number)
        db.add(player)
        db.commit()
        db.refresh(player)
    return player


def detect_and_record_changes(db, team: Team, current_players: List[Dict]):
    latest_snapshot = (
        db.query(Snapshot)
        .filter(Snapshot.team_id == team.id)
        .order_by(Snapshot.captured_at.desc())
        .first()
    )

    prev_names = set()
    if latest_snapshot:
        prev_names = {p.name for p in latest_snapshot.players}

    curr_names = {p["name"] for p in current_players}
    added = curr_names - prev_names
    removed = prev_names - curr_names

    changes_detected = []

    for name in added:
        entry = next(p for p in current_players if p["name"] == name)
        player = get_or_create_player(db, team.id, name, entry.get("number"))
        player.status = "active"
        change = Change(team_id=team.id, player_id=player.id, change_type=ChangeType.added)
        db.add(change)
        changes_detected.append({"type": "added", "player": name})

    for name in removed:
        player = db.query(Player).filter(Player.team_id == team.id, Player.name == name).first()
        if player:
            player.status = "inactive"
            change = Change(team_id=team.id, player_id=player.id, change_type=ChangeType.removed)
            db.add(change)
            changes_detected.append({"type": "removed", "player": name})

    # Create new snapshot
    snapshot = Snapshot(team_id=team.id, captured_at=datetime.now(timezone.utc))
    db.add(snapshot)
    db.commit()
    db.refresh(snapshot)

    # Associate current players with snapshot
    for pd in current_players:
        player = get_or_create_player(db, team.id, pd["name"], pd.get("number"))
        snapshot.players.append(player)
    db.commit()

    return changes_detected


def run_scraper():
    init_db()
    db = SessionLocal()
    try:
        for event_id in SEED_EVENT_IDS:
            event_id = event_id.strip()
            if not event_id:
                continue
            log.info("Processing event: %s", event_id)
            team_entries = parse_whos_coming(event_id)

            for team_data in team_entries:
                team = upsert_team(db, team_data)
                current_players = parse_roster(team.roster_url)
                if not current_players:
                    log.warning("No players found for %s", team.name)
                    continue

                changes = detect_and_record_changes(db, team, current_players)
                if changes:
                    log.info("Changes for %s: %s", team.name, changes)
                    post_slack_notification(team, changes)
    finally:
        db.close()


if __name__ == "__main__":
    run_scraper()
