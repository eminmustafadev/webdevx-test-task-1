import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ..app.main import app
from ..app.database import Base, get_db

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

from unittest.mock import patch

@pytest.fixture(scope="function")
def mock_gemini():
    with patch("app.services.generate_tasks") as mock:
        mock.return_value = ["Test Task 1", "Test Task 2", "Test Task 3"]
        yield mock

# Fixtures
@pytest.fixture(scope="function")
def test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(test_db):
    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()

# Test cases
def test_create_project(client, mock_gemini):
    response = client.post(
        "/projects/",
        json={"project_name": "Test Project", "location": "Test Location"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["project_name"] == "Test Project"
    assert data["location"] == "Test Location"
    assert data["status"] == "in_progress"
    assert all(task["status"] == "pending" for task in data["tasks"])

def test_get_project(client, mock_gemini):
    create_response = client.post("/projects/", json={
        "project_name": "Test Get",
        "location": "Test City"
    })
    project_id = create_response.json()["id"]

    response = client.get(f"/projects/{project_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == project_id
    assert data["status"] == "in_progress"

def test_get_nonexistent_project(client):
    response = client.get("/projects/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Project not found"

def test_task_progression(client, mock_gemini):
    create_response = client.post("/projects/", json={
        "project_name": "Progress Test",
        "location": "Test City"
    })
    project_id = create_response.json()["id"]

    initial_response = client.get(f"/projects/{project_id}")
    assert initial_response.json()["status"] == "in_progress"

    import time
    time.sleep(7)

    progressed_response = client.get(f"/projects/{project_id}")
    progressed_data = progressed_response.json()

    assert progressed_data["status"] in ["in_progress", "completed"]

def test_invalid_project_creation(client):
    response = client.post("/projects/", json={"invalid": "data"})
    assert response.status_code == 422
