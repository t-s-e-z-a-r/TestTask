import pytest
from fastapi import status
from httpx import AsyncClient
from conftest import auth_headers


@pytest.mark.asyncio
async def test_create_post(ac: AsyncClient, auth_headers):
    response = await ac.post(
        "/api/posts/",
        json={"title": "Test Post", "text": "This is a test post"},
        headers=auth_headers,
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["title"] == "Test Post"
    assert data["text"] == "This is a test post"


@pytest.mark.asyncio
async def test_get_posts(ac: AsyncClient):
    response = await ac.get("/api/posts/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) > 0


@pytest.mark.asyncio
async def test_get_post(ac: AsyncClient):
    response = await ac.get(f"/api/posts/1")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["title"] == "Test Post 0"
    assert data["text"] == "This is a test post"


@pytest.mark.asyncio
async def test_create_post_blocked(ac: AsyncClient, auth_headers):
    response = await ac.post(
        "/api/posts/",
        json={"title": "Blocked Post", "text": "This is a toxic post"},
        headers=auth_headers,
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {
        "detail": "Your post has been blocked because of toxic content."
    }


@pytest.mark.asyncio
async def test_update_post(ac: AsyncClient, auth_headers):
    response = await ac.put(
        f"/api/posts/1",
        json={"title": "Updated Post", "text": "This is an updated test post"},
        headers=auth_headers,
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["title"] == "Updated Post"
    assert data["text"] == "This is an updated test post"


@pytest.mark.asyncio
async def test_update_post_blocked(ac: AsyncClient, auth_headers):
    response = await ac.put(
        "/api/posts/2",
        json={"title": "Updated Blocked Post", "text": "This is a toxic updated post"},
        headers=auth_headers,
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {
        "detail": "Your post has been blocked because of toxic content."
    }


@pytest.mark.asyncio
async def test_delete_post(ac: AsyncClient, auth_headers):
    response = await ac.delete("/api/posts/2", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["msg"] == "Post successfully deleted"


@pytest.mark.asyncio
async def test_get_post_not_found(ac: AsyncClient, auth_headers):
    response = await ac.get("/api/posts/999", headers=auth_headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Post not found"}


@pytest.mark.asyncio
async def test_update_post_not_found(ac: AsyncClient, auth_headers):
    response = await ac.put(
        "/api/posts/999",
        json={"title": "Non-existent Post", "text": "This post does not exist"},
        headers=auth_headers,
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Post not found"}


@pytest.mark.asyncio
async def test_delete_post_not_found(ac: AsyncClient, auth_headers):
    response = await ac.delete("/api/posts/999", headers=auth_headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Post not found"}
