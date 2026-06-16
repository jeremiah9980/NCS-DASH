import logging
import json
import requests
from app.config import settings

log = logging.getLogger(__name__)


def post_slack_notification(team, changes: list):
    """Post a Slack message summarizing roster changes for a team."""
    if not settings.slack_webhook_url:
        log.debug("Slack webhook not configured; skipping notification")
        return

    added = [c["player"] for c in changes if c["type"] == "added"]
    removed = [c["player"] for c in changes if c["type"] == "removed"]

    lines = [f"*Roster update for {team.name}* ({team.division})"]
    if added:
        lines.append(f":green_circle: Added: {', '.join(added)}")
    if removed:
        lines.append(f":red_circle: Removed: {', '.join(removed)}")

    payload = {"text": "\n".join(lines)}
    try:
        resp = requests.post(
            settings.slack_webhook_url,
            data=json.dumps(payload),
            headers={"Content-Type": "application/json"},
            timeout=10,
        )
        resp.raise_for_status()
    except Exception as e:
        log.error("Failed to send Slack notification: %s", e)
