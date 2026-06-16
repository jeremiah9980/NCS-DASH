from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base


class Team(Base):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, index=True)
    ncs_id = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    division = Column(String, nullable=False)
    city = Column(String, nullable=True)
    region = Column(String, nullable=True)
    roster_url = Column(String, nullable=True)

    players = relationship("Player", back_populates="team", cascade="all, delete-orphan")
    snapshots = relationship("Snapshot", back_populates="team", cascade="all, delete-orphan")
    changes = relationship("Change", back_populates="team", cascade="all, delete-orphan")
