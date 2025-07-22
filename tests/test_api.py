from unittest.mock import patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.database import sample_collection
from app.main import app
from app.services import get_date_format


@pytest.mark.asyncio
async def test_aggregate_salary(client, mock_aggregate, valid_request_data):
    """ Проверка успешной агрегации """
    with patch.object(sample_collection, "aggregate", return_value=mock_aggregate):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.post("/salaries/aggregate", json=valid_request_data)
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
