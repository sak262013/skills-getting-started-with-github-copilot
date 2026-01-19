import pytest
from fastapi.testclient import TestClient

def test_get_activities(client: TestClient):
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "Programming Class" in data

    # Check structure of activity data
    chess_club = data["Chess Club"]
    assert "description" in chess_club
    assert "schedule" in chess_club
    assert "max_participants" in chess_club
    assert "participants" in chess_club
    assert isinstance(chess_club["participants"], list)

def test_signup_for_activity(client: TestClient):
    # Test successful signup
    response = client.post("/activities/Chess%20Club/signup?email=test@example.com")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "Signed up test@example.com for Chess Club" in data["message"]

    # Verify the participant was added
    response = client.get("/activities")
    data = response.json()
    assert "test@example.com" in data["Chess Club"]["participants"]

def test_signup_already_signed_up(client: TestClient):
    # First signup
    client.post("/activities/Chess%20Club/signup?email=duplicate@example.com")

    # Try to signup again
    response = client.post("/activities/Chess%20Club/signup?email=duplicate@example.com")
    assert response.status_code == 400
    data = response.json()
    assert "Student already signed up" in data["detail"]

def test_signup_activity_full(client: TestClient):
    # Fill up an activity
    activity = "Chess Club"
    max_participants = 12  # From the app data

    # Add participants up to max
    for i in range(max_participants):
        email = f"user{i}@example.com"
        client.post(f"/activities/{activity}/signup?email={email}")

    # Try to add one more
    response = client.post(f"/activities/{activity}/signup?email=overflow@example.com")
    assert response.status_code == 400
    data = response.json()
    assert "Activity is full" in data["detail"]

def test_signup_nonexistent_activity(client: TestClient):
    response = client.post("/activities/Nonexistent%20Activity/signup?email=test@example.com")
    assert response.status_code == 404
    data = response.json()
    assert "Activity not found" in data["detail"]

def test_unregister_from_activity(client: TestClient):
    # First signup
    client.post("/activities/Programming%20Class/signup?email=unregister@example.com")

    # Then unregister
    response = client.delete("/activities/Programming%20Class/unregister?email=unregister@example.com")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "Unregistered unregister@example.com from Programming Class" in data["message"]

    # Verify the participant was removed
    response = client.get("/activities")
    data = response.json()
    assert "unregister@example.com" not in data["Programming Class"]["participants"]

def test_unregister_not_signed_up(client: TestClient):
    response = client.delete("/activities/Chess%20Club/unregister?email=notsignedup@example.com")
    assert response.status_code == 400
    data = response.json()
    assert "Student is not signed up for this activity" in data["detail"]

def test_unregister_nonexistent_activity(client: TestClient):
    response = client.delete("/activities/Nonexistent%20Activity/unregister?email=test@example.com")
    assert response.status_code == 404
    data = response.json()
    assert "Activity not found" in data["detail"]