import copy
import pytest

from fastapi.testclient import TestClient

from src import app as app_module


@pytest.fixture(scope="module")
def client():
    """Create a TestClient for the FastAPI app."""
    client = TestClient(app_module.app)
    yield client


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset the in-memory `activities` dict before each test (Arrange).

    This ensures tests are isolated and deterministic.
    """
    original = copy.deepcopy(app_module.activities)
    # Before test: restore snapshot
    app_module.activities.clear()
    app_module.activities.update(copy.deepcopy(original))
    yield
    # After test: restore snapshot again
    app_module.activities.clear()
    app_module.activities.update(copy.deepcopy(original))


def test_get_activities(client):
    # Arrange: client fixture and reset_activities autouse

    # Act
    resp = client.get("/activities")

    # Assert
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    assert len(data) > 0


def test_signup_adds_participant(client):
    # Arrange
    activity_name = "Gym Class"
    test_email = "unittest@example.com"
    # ensure not present
    participants = app_module.activities[activity_name]["participants"]
    if test_email in participants:
        participants.remove(test_email)

    # Act
    resp = client.post(f"/activities/{activity_name}/signup?email={test_email}")

    # Assert
    assert resp.status_code == 200
    assert test_email in app_module.activities[activity_name]["participants"]


def test_unregister_removes_participant(client):
    # Arrange
    activity_name = "Soccer Team"
    test_email = "remove_me@example.com"
    participants = app_module.activities[activity_name]["participants"]
    if test_email not in participants:
        participants.append(test_email)

    # Act
    resp = client.post(f"/activities/{activity_name}/unregister?email={test_email}")

    # Assert
    assert resp.status_code == 200
    assert test_email not in app_module.activities[activity_name]["participants"]
