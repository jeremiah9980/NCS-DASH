from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models.team import Team
from app.models.player import Player
from app.models.snapshot import Snapshot
from app.models.change import Change
from app.schemas.team import TeamRead, TeamCreate
from app.schemas.player import PlayerRead
from app.schemas.change import ChangeRead

router = APIRouter(prefix="/teams", tags=["teams"])


@router.get("", response_model=List[TeamRead])
def list_teams(
    division: Optional[str] = None,
    city: Optional[str] = None,
    db: Session = Depends(get_db),
):
    q = db.query(Team)
    if division:
        q = q.filter(Team.division.ilike(f"%{division}%"))
    if city:
        q = q.filter(Team.city.ilike(f"%{city}%"))
    return q.order_by(Team.name).all()


@router.post("", response_model=TeamRead, status_code=201)
def create_team(team: TeamCreate, db: Session = Depends(get_db)):
    existing = db.query(Team).filter(Team.ncs_id == team.ncs_id).first()
    if existing:
        raise HTTPException(status_code=409, detail="Team already exists")
    db_team = Team(**team.model_dump())
    db.add(db_team)
    db.commit()
    db.refresh(db_team)
    return db_team


@router.get("/{team_id}", response_model=TeamRead)
def get_team(team_id: int, db: Session = Depends(get_db)):
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    return team


@router.get("/{team_id}/roster", response_model=List[PlayerRead])
def get_roster(team_id: int, db: Session = Depends(get_db)):
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    return db.query(Player).filter(Player.team_id == team_id, Player.status == "active").all()


@router.get("/{team_id}/history", response_model=List[ChangeRead])
def get_history(
    team_id: int,
    limit: int = Query(50, le=200),
    db: Session = Depends(get_db),
):
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    changes = (
        db.query(Change)
        .filter(Change.team_id == team_id)
        .order_by(Change.change_time.desc())
        .limit(limit)
        .all()
    )
    result = []
    for c in changes:
        result.append(
            ChangeRead(
                id=c.id,
                team_id=c.team_id,
                player_id=c.player_id,
                player_name=c.player.name if c.player else "Unknown",
                change_type=c.change_type,
                change_time=c.change_time,
            )
        )
    return result
