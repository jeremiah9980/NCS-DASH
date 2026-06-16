from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional, List

from app.database import get_db
from app.models.team import Team
from app.models.player import Player
from app.schemas.team import TeamRead
from app.schemas.player import PlayerRead

router = APIRouter(prefix="/search", tags=["search"])


@router.get("/teams", response_model=List[TeamRead])
def search_teams(
    q: Optional[str] = Query(None, description="Search by team name"),
    division: Optional[str] = None,
    city: Optional[str] = None,
    db: Session = Depends(get_db),
):
    query = db.query(Team)
    if q:
        query = query.filter(Team.name.ilike(f"%{q}%"))
    if division:
        query = query.filter(Team.division.ilike(f"%{division}%"))
    if city:
        query = query.filter(Team.city.ilike(f"%{city}%"))
    return query.order_by(Team.name).limit(25).all()


@router.get("/players", response_model=List[PlayerRead])
def search_players(
    q: Optional[str] = Query(None, description="Search by player name"),
    team_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    query = db.query(Player)
    if q:
        query = query.filter(Player.name.ilike(f"%{q}%"))
    if team_id:
        query = query.filter(Player.team_id == team_id)
    return query.limit(50).all()
