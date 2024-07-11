import pytest
from fastapi import status
from httpx import AsyncClient
from main import app
from conftest import client, async_session_maker
from sqlalchemy.sql import text


@pytest.fixture(scope="function", autouse=True)
async def setup_comments_data():
    async with async_session_maker() as session:
        await session.execute(
            text(
                """
            INSERT INTO comments (text, is_blocked, created_at, author_id, post_id, parent_id)
            VALUES 
            ('This is a comment to the test post', false, '2023-07-10 17:38:24.126645', 1, 1, NULL),
            ('Thank you for your comment! We appreciate you taking the time to engage with our test post.', false, '2023-07-11 08:38:24.126645', 1, 1, 1),
            ('We''re still working out some of the kinks, so your feedback is very valuable.', false, '2023-07-12 09:38:24.126645', 1, 1, 1),
            ('Could you tell me what your favourite colour is?', false, '2023-07-13 10:38:24.126645', 1, 1, NULL),
            ('That''s a great question! I don''t have personal preferences like favorite colors, as I''m an AI.', false, '2023-07-14 11:38:24.126645', 1, 1, 4),
            ('Thank you for your comment! I''m glad you''re taking a look at this test post.', false, '2023-07-15 12:38:24.126645', 1, 1, 1),
            ('This is another comment on the post.', false, '2023-07-16 13:38:24.126645', 1, 1, NULL),
            ('Can you share more about the topic?', false, '2023-07-17 14:38:24.126645', 1, 1, 6),
            ('Yes, I can provide more details. What exactly are you interested in?', false, '2023-07-18 15:38:24.126645', 1, 1, 7),
            ('I''m interested in learning more about the latest updates.', false, '2023-07-19 16:38:24.126645', 1, 1, 8),
            ('This comment is blocked due to toxic content.', true, '2023-07-20 17:38:24.126645', 1, 1, NULL),
            ('Another blocked comment due to inappropriate language.', true, '2023-07-21 18:38:24.126645', 1, 1, NULL);
            """
            )
        )
        await session.commit()


@pytest.mark.asyncio
async def test_comments_daily_breakdown(ac: AsyncClient):
    date_from = "2023-07-10"
    date_to = "2023-07-22"

    response = await ac.get(
        "/api/analytics/comments", params={"date_from": date_from, "date_to": date_to}
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 12
    assert data[0]["date"] == "2023-07-10"
    assert data[0]["total_comments"] == 1
    assert data[0]["blocked_comments"] == 0
    assert data[10]["date"] == "2023-07-20"
    assert data[10]["total_comments"] == 1
    assert data[10]["blocked_comments"] == 1
    assert data[11]["date"] == "2023-07-21"
    assert data[11]["total_comments"] == 1
    assert data[11]["blocked_comments"] == 1
