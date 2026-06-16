from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Player(Base):
    __tablename__ = "players"

    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    name = Column(String, nullable=False)
    number = Column(String, nullable=True)
    status = Column(String, default="active")

    team = relationship("Team", back_populates="players")
    changes = relationship("Change", back_populates="player")
