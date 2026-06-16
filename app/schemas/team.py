from pydantic import BaseModel
from typing import Optional


class TeamBase(BaseModel):
    ncs_id: str
    name: str
    division: str
    city: Optional[str] = None
    region: Optional[str] = None
    roster_url: Optional[str] = None


class TeamCreate(TeamBase):
    pass


class TeamRead(TeamBase):
    id: int

    class Config:
        from_attributes = True
