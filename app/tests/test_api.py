# import pytest
# from httpx import AsyncClient, ASGITransport
#
# from app.main import app
#
# @pytest.mark.asyncio
# async def test_aggregate_salary():
#     async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
#         headers = {"dt_from": "2022-09-01T00:00:00", "dt_upto": "2022-12-31T23:59:00", "group_type": "month"}
#         response = await ac.post("/salaries/aggregate", json=headers)
#         print(response.status_code, response.json())
