from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime
from typing import Any, Dict

from app.database import get_db
from app.schemas.change import AgentQuery
from app.models.team import Team
from app.models.player import Player
from app.models.change import Change

router = APIRouter(prefix="/agent", tags=["agent"])


@router.post("/query")
def agent_query(query: AgentQuery, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Accepts a structured JSON query and returns matching roster or change records.
    Supports: team name, player name, division, city, date range.
    """
    filters = []

    team_ids = None
    if query.team or query.division or query.city:
        team_q = db.query(Team.id)
        if query.team:
            team_q = team_q.filter(Team.name.ilike(f"%{query.team}%"))
        if query.division:
            team_q = team_q.filter(Team.division.ilike(f"%{query.division}%"))
        if query.city:
            team_q = team_q.filter(Team.city.ilike(f"%{query.city}%"))
        team_ids = [r[0] for r in team_q.all()]
        if not team_ids:
            return {"results": [], "message": "No teams matched the query."}
        filters.append(Change.team_id.in_(team_ids))

    if query.player:
        player_ids = [
            r[0]
            for r in db.query(Player.id).filter(Player.name.ilike(f"%{query.player}%")).all()
        ]
        if not player_ids:
            return {"results": [], "message": "No players matched the query."}
        filters.append(Change.player_id.in_(player_ids))

    if query.date_from:
        filters.append(Change.change_time >= datetime.fromisoformat(query.date_from))
    if query.date_to:
        filters.append(Change.change_time <= datetime.fromisoformat(query.date_to))

    changes = db.query(Change).filter(and_(*filters) if filters else True).order_by(Change.change_time.desc()).limit(100).all()

    results = [
        {
            "change_id": c.id,
            "team": c.team.name if c.team else None,
            "division": c.team.division if c.team else None,
            "player": c.player.name if c.player else None,
            "change_type": c.change_type,
            "change_time": c.change_time.isoformat() if c.change_time else None,
        }
        for c in changes
    ]

    return {
        "query": query.model_dump(),
        "count": len(results),
        "results": results,
    }
