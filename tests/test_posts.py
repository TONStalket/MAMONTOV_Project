"""Tests for post and follow functionality."""

from fastapi import status


def authenticate(client, email: str, password: str) -> str:
    response = client.post(
        "/auth/token",
        data={"username": email, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == status.HTTP_200_OK
    return response.json()["access_token"]


def test_create_post_and_feed(client, create_user):
    token = authenticate(client, create_user["email"], create_user["password"])
    headers = {"Authorization": f"Bearer {token}"}

    create_response = client.post("/posts/", json={"content": "Hello world"}, headers=headers)
    assert create_response.status_code == status.HTTP_201_CREATED
    post_data = create_response.json()
    assert post_data["content"] == "Hello world"

    feed_response = client.get("/posts/", headers=headers)
    assert feed_response.status_code == status.HTTP_200_OK
    feed = feed_response.json()
    assert len(feed["posts"]) == 1
    assert feed["posts"][0]["content"] == "Hello world"


def test_follow_user_and_view_network(client, create_user, session):
    # create second user
    second_user_payload = {
        "email": "friend@example.com",
        "username": "friend",
        "password": "friendpass",
    }
    register_response = client.post("/auth/register", json=second_user_payload)
    assert register_response.status_code == status.HTTP_201_CREATED
    second_user_id = register_response.json()["id"]

    token = authenticate(client, create_user["email"], create_user["password"])
    headers = {"Authorization": f"Bearer {token}"}

    follow_response = client.post(f"/users/{second_user_id}/follow", headers=headers)
    assert follow_response.status_code == status.HTTP_200_OK
    assert follow_response.json()["id"] == second_user_id

    network_response = client.get(f"/users/{second_user_id}/network", headers=headers)
    assert network_response.status_code == status.HTTP_200_OK
    network = network_response.json()
    assert any(user["id"] == create_user["instance"].id for user in network["followers"])
