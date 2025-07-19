from pydantic import BaseModel
from datetime import datetime


class SalaryAggregationRequest(BaseModel):
    """ Входные данные для получения информации о зарплате. """
    dt_from: datetime
    dt_upto: datetime
    group_type: str


class SalaryAggregationResponse(BaseModel):
    """ Выходные данные после агрегации данных. """
    dataset: list[float]
    labels: list[str]