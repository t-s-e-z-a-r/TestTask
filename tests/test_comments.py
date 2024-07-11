import pytest
from fastapi import status
from httpx import AsyncClient
from database.models import Comment
from database.config import async_session_maker
from celery_app.worker import _create_auto_response_comment
from sqlalchemy.future import select


@pytest.mark.asyncio
async def test_create_comment(ac: AsyncClient, auth_headers):
    response = await ac.post(
        "/api/comments/",
        json={"text": "This is a test comment", "post_id": 1},
        headers=auth_headers,
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["text"] == "This is a test comment"


@pytest.mark.asyncio
async def test_get_comments(ac: AsyncClient):
    response = await ac.get("/api/comments/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) > 0


@pytest.mark.asyncio
async def test_get_comment(ac: AsyncClient):
    response = await ac.get(f"/api/comments/1")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["text"] == "This is a test comment for post 0"


@pytest.mark.asyncio
async def test_create_reply(ac: AsyncClient, auth_headers):
    response = await ac.post(
        "/api/comments/",
        json={"text": "This is a test reply", "post_id": 1, "parent_id": 1},
        headers=auth_headers,
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["text"] == "This is a test reply"
    assert data["parent_id"] == 1


@pytest.mark.asyncio
async def test_create_reply_with_mismatched_post_id(ac: AsyncClient, auth_headers):
    response = await ac.post(
        "/api/comments/",
        json={
            "text": "This is a mismatched post ID reply",
            "post_id": 2,
            "parent_id": 1,
        },
        headers=auth_headers,
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {
        "detail": "Post ID of the reply does not match the parent comment's post ID"
    }


@pytest.mark.asyncio
async def test_create_reply_with_nonexistent_parent(ac: AsyncClient, auth_headers):
    response = await ac.post(
        "/api/comments/",
        json={
            "text": "This is a reply to a non-existent comment",
            "post_id": 1,
            "parent_id": 999,
        },
        headers=auth_headers,
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Parent comment not found"}


@pytest.mark.asyncio
async def test_update_comment(ac: AsyncClient, auth_headers):
    response = await ac.put(
        f"/api/comments/1",
        json={"text": "Updated test comment"},
        headers=auth_headers,
    )
    assert (
        response.status_code == status.HTTP_200_OK
    ), f"Expected status 200, got {response.status_code}. Response: {response.json()}"
    data = response.json()
    assert data["text"] == "Updated test comment"


@pytest.mark.asyncio
async def test_update_comment_blocked(ac: AsyncClient, auth_headers):
    response = await ac.put(
        "/api/comments/2",
        json={"text": "This is a toxic updated comment"},
        headers=auth_headers,
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {
        "detail": "Your comment has been blocked because of toxic content."
    }


@pytest.mark.asyncio
async def test_delete_comment(ac: AsyncClient, auth_headers):
    response = await ac.delete("/api/comments/2", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["msg"] == "Comment successfully deleted"


@pytest.mark.asyncio
async def test_get_comment_not_found(ac: AsyncClient, auth_headers):
    response = await ac.get("/api/comments/999", headers=auth_headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Comment not found"}


@pytest.mark.asyncio
async def test_update_comment_not_found(ac: AsyncClient, auth_headers):
    response = await ac.put(
        "/api/comments/999",
        json={"text": "Non-existent comment"},
        headers=auth_headers,
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Comment not found"}


@pytest.mark.asyncio
async def test_delete_comment_not_found(ac: AsyncClient, auth_headers):
    response = await ac.delete("/api/comments/999", headers=auth_headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Comment not found"}
