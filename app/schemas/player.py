from pydantic import BaseModel
from typing import Optional


class PlayerBase(BaseModel):
    name: str
    number: Optional[str] = None
    status: str = "active"


class PlayerCreate(PlayerBase):
    team_id: int


class PlayerRead(PlayerBase):
    id: int
    team_id: int

    class Config:
        from_attributes = True
