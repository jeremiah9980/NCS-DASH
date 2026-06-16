from pydantic import BaseModel
from datetime import datetime
from app.models.change import ChangeType


class ChangeRead(BaseModel):
    id: int
    team_id: int
    player_id: int
    player_name: str
    change_type: ChangeType
    change_time: datetime

    class Config:
        from_attributes = True


class AgentQuery(BaseModel):
    team: str | None = None
    player: str | None = None
    division: str | None = None
    city: str | None = None
    date_from: str | None = None
    date_to: str | None = None
