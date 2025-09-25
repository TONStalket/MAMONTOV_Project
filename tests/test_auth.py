"""Tests for authentication endpoints."""

from fastapi import status


def test_register_and_login(client):
    response = client.post(
        "/auth/register",
        json={
            "email": "newuser@example.com",
            "username": "newuser",
            "password": "password123",
        },
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert "id" in data

    login_response = client.post(
        "/auth/token",
        data={"username": "newuser@example.com", "password": "password123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert login_response.status_code == status.HTTP_200_OK
    token_data = login_response.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"


def test_register_duplicate_email(client):
    payload = {
        "email": "dupe@example.com",
        "username": "uniqueuser",
        "password": "password123",
    }
    assert client.post("/auth/register", json=payload).status_code == status.HTTP_201_CREATED
    response = client.post("/auth/register", json=payload)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
