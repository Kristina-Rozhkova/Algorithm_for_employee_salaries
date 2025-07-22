import pytest_asyncio
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from aiogram import Dispatcher, Bot
from aiogram.fsm.storage.memory import MemoryStorage


@pytest_asyncio.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
