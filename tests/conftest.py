from datetime import datetime
from unittest.mock import AsyncMock

import pytest
import pytest_asyncio
from aiogram import types
from aiogram.fsm.context import FSMContext
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest_asyncio.fixture
async def client():
    """ Генератор клиента """
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac


@pytest.fixture
def mock_aggregate_data():
    """ Фикстура с тестовыми данными для агрегации """
    return [
        {
            "_id": "2021-12-31T03:00:00",
            "total": 295,
            "dt_first": datetime(2022, 1, 1, 3, 28)
        },
        {
            "_id": "2021-12-31T04:00:00",
            "total": 512,
            "dt_first": datetime(2021, 12, 31, 22, 56)
        }
    ]


@pytest.fixture
def mock_aggregate(mock_aggregate_data):
    """ Фикстура для мока агрегации """
    mock_cursor = AsyncMock()
    mock_cursor.to_list.return_value = mock_aggregate_data
    return mock_cursor


@pytest.fixture
def valid_request_data():
    """ Фикстура с валидными данными запроса """
    return {
        "dt_from": "2021-12-31T02:00:00",
        "dt_upto": "2021-12-31T04:00:00",
        "group_type": "hour"
    }


@pytest.fixture
def message():
    """ Фикстура для создания mock-сообщения """
    msg = AsyncMock(spec=types.Message)
    msg.answer = AsyncMock()
    return msg


@pytest.fixture
def state():
    """ Фикстура для создания mock-состояния """
    st = AsyncMock(spec=FSMContext)
    st.update_data = AsyncMock()
    st.set_state = AsyncMock()
    st.get_data = AsyncMock(return_value={})
    return st


@pytest.fixture
def callback():
    """ Фикстура для создания mock-callback """
    cb = AsyncMock(spec=types.CallbackQuery)
    cb.message = AsyncMock()
    cb.message.answer = AsyncMock()
    cb.answer = AsyncMock()
    return cb
