from fastapi import FastAPI, HTTPException
import uvicorn
from app.services import get_date_grouping
from database import db
from app.models import SalaryAggregationRequest, SalaryAggregationResponse

app = FastAPI()

@app.post("/aggregate", tags=["Зарплата"], summary="Запрос информации по зарплате", response_model=SalaryAggregationResponse)
async def aggregate_salary(request: SalaryAggregationRequest):
    group_by_dt = get_date_grouping(request.group_type)

    pipeline = [
        {
            "$match": {
                "dt": {
                    "$gte": request.dt_from,
                    "$lte": request.dt_upto
                }
            }
        },
        {
            "$group": {
                "_id": group_by_dt,
                "total": {"$sum": "$value"},
                "dt_first": {"$first": "$dt"}
            }
        },
        {
            "$sort": {"_id": 1}
        }
    ]

    try:
        cursor = db.sample_collection.aggregate(pipeline)
        aggregated_data = await cursor.to_list(length=None)

        dataset = [item["total"] for item in aggregated_data]
        labels = [item["_id"] for item in aggregated_data]

        return {"dataset": dataset, "labels": labels}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)