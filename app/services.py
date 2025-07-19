from fastapi import HTTPException


def get_date_grouping(group_type):
    """ Группировка выплат сотрудников по определенному промежутку времени: час, день, месяц """
    if group_type == "hour":
        return {"$dateToString": {"format": "%Y-%m-%dT%H:00:00", "date": "$dt"}}
    elif group_type == "day":
        return {"$dateToString": {"format": "%Y-%m-%dT00:00:00", "date": "$dt"}}
    elif group_type == "month":
        return {"$dateToString": {"format": "%Y-%m-01T00:00:00", "date": "$dt"}}
    raise HTTPException(status_code=400, detail="Invalid group type. Must be 'hour', 'day' or 'month'.")