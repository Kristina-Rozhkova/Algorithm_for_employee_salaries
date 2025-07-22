from fastapi import HTTPException


def get_date_format(group_type: str) -> dict:
    """ Преобразование формата дат в соответствии с выбранной группировкой: час, день, месяц """
    if group_type not in ["hour", "day", "month"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid group type. Must be 'hour', 'day' or 'month'.",
        )
    formats = {
        "hour": "%Y-%m-%dT%H:00:00",
        "day": "%Y-%m-%dT00:00:00",
        "month": "%Y-%m-01T00:00:00",
    }
    return {"$dateToString": {"format": formats[group_type], "date": "$dt"}}
