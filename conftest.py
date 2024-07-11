import pytest

from fastapi.testclient import TestClient

from httpx import AsyncClient

from decouple import config

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
import time
from database.config import (
    get_async_session,
    metadata,
    DB_HOST,
    DB_USER,
    DB_PASS,
    DB_PORT,
)
from database.models import Post, Comment
from main import app

DB_NAME_TEST = config("DB_NAME_TEST")

DATABASE_URL_TEST = (
    f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME_TEST}"
)

engine_test = create_async_engine(DATABASE_URL_TEST, poolclass=NullPool)
async_session_maker = sessionmaker(
    engine_test, class_=AsyncSession, expire_on_commit=False
)
metadata.bind = engine_test


async def override_get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


app.dependency_overrides[get_async_session] = override_get_async_session


@pytest.fixture(scope="session", autouse=True)
async def prepare_database():
    time.sleep(45) # To avoid database starting up error
    async with engine_test.begin() as conn:
        await conn.run_sync(metadata.create_all)
    yield
    async with engine_test.begin() as conn:
        await conn.run_sync(metadata.drop_all)


client = TestClient(app)


@pytest.fixture(scope="session")
async def ac() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture(scope="session")
async def auth_headers(ac: AsyncClient):
    response = await ac.post(
        "/auth/register", json={"username": "testuser", "password": "testpassword"}
    )
    response = await ac.post(
        "/auth/login", json={"username": "testuser", "password": "testpassword"}
    )
    async with async_session_maker() as session:
        for i in range(0, 2):
            post = Post(title=f"Test Post {i}", text="This is a test post", author_id=1)
            session.add(post)
            await session.commit()
            await session.refresh(post)

            comment = Comment(
                text=f"This is a test comment for post {i}",
                author_id=1,
                post_id=post.id,
            )
            session.add(comment)
            await session.commit()
            await session.refresh(comment)
    data = response.json()
    access_token = data["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}
    return headers
