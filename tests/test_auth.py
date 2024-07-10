import pytest
from fastapi import status
from httpx import AsyncClient
from main import app
from conftest import client, async_session_maker


@pytest.mark.asyncio
async def test_register_user(ac: AsyncClient, auth_headers):
    response = await ac.post(
        "/auth/register", json={"username": "testuser2", "password": "testpassword"}
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"msg": "User successfully registered"}


@pytest.mark.asyncio
async def test_register_user_already_exists(ac: AsyncClient):
    response = await ac.post(
        "/auth/register", json={"username": "testuser2", "password": "testpassword"}
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"detail": "Username already registered"}


@pytest.mark.asyncio
async def test_login_user(ac: AsyncClient):
    response = await ac.post(
        "/auth/login", json={"username": "testuser2", "password": "testpassword"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_user_invalid_credentials(ac: AsyncClient):
    response = await ac.post(
        "/auth/login", json={"username": "invaliduser", "password": "wrongpassword"}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Invalid username or password"}


@pytest.mark.asyncio
async def test_login_user_invalid_password(ac: AsyncClient):
    response = await ac.post(
        "/auth/login", json={"username": "testuser", "password": "wrongpassword"}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Invalid username or password"}


@pytest.mark.asyncio
async def test_update_user_auto_respond(ac: AsyncClient, auth_headers):
    response = await ac.put(
        "/auth/user",
        json={"auto_respond": True},
        headers=auth_headers,
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["msg"] == "User updated successfully"


@pytest.mark.asyncio
async def test_update_user_respond_time(ac: AsyncClient, auth_headers):
    response = await ac.put(
        "/auth/user",
        json={"respond_time": 5},
        headers=auth_headers,
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["msg"] == "User updated successfully"


@pytest.mark.asyncio
async def test_update_user_respond_time_zero(ac: AsyncClient, auth_headers):
    response = await ac.put(
        "/auth/user",
        json={"respond_time": 0},
        headers=auth_headers,
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    data = response.json()
    assert data["detail"] == "Respond time must be greater than 0"


@pytest.mark.asyncio
async def test_update_user_respond_time_negative(ac: AsyncClient, auth_headers):
    response = await ac.put(
        "/auth/user",
        json={"respond_time": -1},
        headers=auth_headers,
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    data = response.json()
    assert data["detail"] == "Respond time must be greater than 0"


@pytest.mark.asyncio
async def test_update_user_auto_respond_and_respond_time(ac: AsyncClient, auth_headers):
    response = await ac.put(
        "/auth/user",
        json={"auto_respond": True, "respond_time": 5},
        headers=auth_headers,
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["msg"] == "User updated successfully"


@pytest.mark.asyncio
async def test_update_user_auto_respond_disable(ac: AsyncClient, auth_headers):
    response = await ac.put(
        "/auth/user",
        json={"auto_respond": False},
        headers=auth_headers,
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["msg"] == "User updated successfully"


@pytest.mark.asyncio
async def test_update_user_unauthorized(ac: AsyncClient):
    response = await ac.put(
        "/auth/user",
        json={"auto_respond": True, "respond_time": 5},
        headers={"Authorization": "Bearer invalid_token"},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
