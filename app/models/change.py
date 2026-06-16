from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.database import Base


class ChangeType(str, enum.Enum):
    added = "added"
    removed = "removed"


class Change(Base):
    __tablename__ = "changes"

    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False)
    change_type = Column(Enum(ChangeType), nullable=False)
    change_time = Column(DateTime(timezone=True), server_default=func.now())

    team = relationship("Team", back_populates="changes")
    player = relationship("Player", back_populates="changes")
