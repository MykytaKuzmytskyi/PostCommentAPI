import asyncio

import pytest_asyncio
from fastapi import Depends
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from config import settings
from database.database import get_async_session, Base
from database.dependencies import get_db
from src.main import app
from src.user.models import User
from src.user.utils import get_user_db

engine_test = create_async_engine(settings.TEST_DATABASE_URL)

async_session_market = sessionmaker(
    autocommit=False, autoflush=False, bind=engine_test, class_=AsyncSession
)


async def override_get_async_session() -> AsyncSession:
    async with async_session_market() as session:
        yield session


async def override_user_get_db(
    session: AsyncSession = Depends(override_get_async_session),
):
    yield SQLAlchemyUserDatabase(session, User)


async def override_get_db():
    db = async_session_market()
    try:
        yield db
    finally:
        await db.close()


app.dependency_overrides[get_async_session] = override_get_async_session
app.dependency_overrides[get_user_db] = override_user_get_db
app.dependency_overrides[get_db] = override_get_db


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_database():
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        pass


@pytest_asyncio.fixture(scope="session", autouse=True)
def event_loop():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def ac() -> AsyncClient:
    async with AsyncClient(app=app, base_url="http://testserver") as ac:
        yield ac


@pytest_asyncio.fixture(scope="session")
async def auth_client(ac):
    registration_data = {
        "email": "string@string.com",
        "password": "string",
        # "auto_reply_enabled": True,
        "auto_reply_delay": "00:00:10",
    }

    response = await ac.post("/auth/register", json=registration_data)
    assert response.status_code == 201, "Registration failed"
    assert "id" in response.json(), "Response should contain user ID"

    login_data = {
        "username": "string@string.com",
        "password": "string",
    }

    response = await ac.post("/auth/login", data=login_data)
    assert response.status_code == 204, "User login failed"

    cookie_header = response.headers.get("set-cookie")
    assert cookie_header is not None, "No cookie returned on login"

    ac.headers["Cookie"] = cookie_header
    yield ac


@pytest_asyncio.fixture(scope="module")
async def created_post(auth_client):
    data = {"title": "First Test Post", "content": "Test content"}
    response = await auth_client.post("/posts", json=data)
    assert response.status_code == 201
    return response.json()
