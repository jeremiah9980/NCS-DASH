import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_list_teams_empty():
    resp = client.get("/teams")
    assert resp.status_code == 200
    assert resp.json() == []


def test_create_and_get_team():
    payload = {
        "ncs_id": "team-001",
        "name": "CenTex Force",
        "division": "10U",
        "city": "Austin",
        "region": "Central Texas",
        "roster_url": "https://example.com/roster",
    }
    resp = client.post("/teams", json=payload)
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "CenTex Force"
    assert data["id"] == 1

    resp2 = client.get(f"/teams/{data['id']}")
    assert resp2.status_code == 200
    assert resp2.json()["ncs_id"] == "team-001"


def test_create_team_duplicate():
    payload = {"ncs_id": "dup-001", "name": "Test Team", "division": "12U"}
    client.post("/teams", json=payload)
    resp = client.post("/teams", json=payload)
    assert resp.status_code == 409


def test_team_not_found():
    resp = client.get("/teams/999")
    assert resp.status_code == 404


def test_roster_empty():
    payload = {"ncs_id": "r-001", "name": "Roster Test", "division": "10U"}
    team = client.post("/teams", json=payload).json()
    resp = client.get(f"/teams/{team['id']}/roster")
    assert resp.status_code == 200
    assert resp.json() == []


def test_history_empty():
    payload = {"ncs_id": "h-001", "name": "History Test", "division": "12U"}
    team = client.post("/teams", json=payload).json()
    resp = client.get(f"/teams/{team['id']}/history")
    assert resp.status_code == 200
    assert resp.json() == []


def test_search_teams():
    client.post("/teams", json={"ncs_id": "s-001", "name": "Austin Angels", "division": "10U", "city": "Austin"})
    resp = client.get("/search/teams", params={"q": "Austin"})
    assert resp.status_code == 200
    assert len(resp.json()) >= 1


def test_agent_query_no_results():
    resp = client.post("/agent/query", json={"team": "Nonexistent Team XYZ"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["count"] == 0 or "message" in data
