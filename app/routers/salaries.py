from datetime import timedelta

from dateutil.relativedelta import relativedelta
from fastapi import APIRouter, HTTPException

from app.database import sample_collection
from app.models import SalaryAggregationRequest, SalaryAggregationResponse
from app.services import get_date_grouping

router = APIRouter(
    prefix="/salaries", tags=["Зарплаты"], responses={404: {"description": "Not found"}}
)


@router.post(
    "/aggregate",
    summary="Агрегация зарплат по периодам",
    response_model=SalaryAggregationResponse,
    responses={
        200: {
            "content": {
                "application/json": {
                    "example": {
                        "dataset": [1000, 2000, 1500],
                        "labels": [
                            "2022-09-01T00:00:00",
                            "2022-09-02T00:00:00",
                            "2022-09-03T00:00:00",
                        ],
                    }
                }
            }
        },
        400: {
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Invalid group type. Must be 'hour', 'day' or 'month'."
                    }
                }
            }
        },
        500: {
            "content": {
                "application/json": {"example": {"detail": "Internal server error"}}
            }
        },
    },
)
async def aggregate_salary(request: SalaryAggregationRequest):
    """
    Получение агрегированных данных о зарплатах.

    Возвращает данные в формате:
    ```json
    {
        "dataset": [1000, 2000, ...],
        "labels": ["2022-09-01T00:00:00", "2022-09-02T00:00:00", ...]
    }
    ```
    """
    group_by_dt = get_date_grouping(request.group_type)

    pipeline = [
        {"$match": {"dt": {"$gte": request.dt_from, "$lte": request.dt_upto}}},
        {
            "$group": {
                "_id": group_by_dt,
                "total": {"$sum": "$value"},
                "dt_first": {"$first": "$dt"},
            }
        },
        {"$sort": {"_id": 1}},
    ]

    try:
        cursor = sample_collection.aggregate(pipeline)
        rows = await cursor.to_list(length=None)
        totals = {row["_id"]: row["total"] for row in rows}

        step = {
            "hour": timedelta(hours=1),
            "day": timedelta(days=1),
            "month": relativedelta(months=1),
        }[request.group_type]

        dataset, labels = [], []

        current = request.dt_from
        end = request.dt_upto

        while current <= end:
            label = current.isoformat(timespec="seconds")
            labels.append(label)
            dataset.append(totals.get(label, 0))
            current += step

        return {"dataset": dataset, "labels": labels}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
