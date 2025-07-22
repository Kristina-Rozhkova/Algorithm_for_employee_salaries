from datetime import datetime
from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.database import sample_collection
from app.main import app
from app.services import get_date_format


@pytest.mark.asyncio
async def test_aggregate_salary():
    """ Проверка успешной агрегации """
    mock_cursor = AsyncMock()
    mock_cursor.to_list.return_value = [
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

    with patch.object(sample_collection, "aggregate", return_value=mock_cursor):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            request_body = {
                "dt_from": "2021-12-31T02:00:00",
                "dt_upto": "2021-12-31T04:00:00",
                "group_type": "hour"
            }
            response = await ac.post("/salaries/aggregate", json=request_body)
            assert response.status_code == 200
            data = response.json()
            assert len(data["dataset"]) == 3
            assert data["dataset"] == [0, 295, 512]
            assert data["labels"] == ['2021-12-31T02:00:00', '2021-12-31T03:00:00', '2021-12-31T04:00:00']


@pytest.mark.asyncio
async def test_invalid_group_type(client):
    """ Проверка выброса 400 ошибки при неверном типе группировки """
    invalid_request = {
        "dt_from": "2022-09-01T00:00:00",
        "dt_upto": "2022-12-31T23:59:00",
        "group_type": "invalid_type"
    }

    response = await client.post("/salaries/aggregate", json=invalid_request)
    assert response.status_code == 400
    assert "Invalid group type. Must be 'hour', 'day' or 'month'." == response.json()["detail"]


@pytest.mark.asyncio
async def test_date_format_service():
    """ Проверка работы сервисной функции форматирования дат"""
    result = get_date_format("hour")
    assert "$dateToString" in result
    assert result["$dateToString"]["format"] == '%Y-%m-%dT%H:00:00'
