from sqlalchemy import Column, Integer, ForeignKey, DateTime, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

snapshot_players = Table(
    "snapshot_players",
    Base.metadata,
    Column("snapshot_id", Integer, ForeignKey("snapshots.id"), primary_key=True),
    Column("player_id", Integer, ForeignKey("players.id"), primary_key=True),
)


class Snapshot(Base):
    __tablename__ = "snapshots"

    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    captured_at = Column(DateTime(timezone=True), server_default=func.now())

    team = relationship("Team", back_populates="snapshots")
    players = relationship("Player", secondary=snapshot_players)
