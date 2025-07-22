from datetime import datetime

from aiogram.fsm.state import State, StatesGroup
from pydantic import BaseModel


class SalaryAggregationRequest(BaseModel):
    """
    Входные данные для получения информации о зарплате за определенный период.

    Аргументы:
    dt_from: Начальная дата (например, '2022-09-01T00:00:00')
    dt_upto: Конечная дата (например, '2022-10-01T00:00:00')
    group_type: Тип группировки зарплаты ('hour' - часовая, 'day' - дневная, 'month' - месячная)
    """

    dt_from: datetime
    dt_upto: datetime
    group_type: str


class SalaryAggregationResponse(BaseModel):
    """
    Выходные данные после агрегации данных.

    Аргументы:
    dataset: список начисленной суммы за определенный период
    labels: список меток времени в формате ISO 8601, соответствующих элементам dataset.
    """

    dataset: list[int]
    labels: list[str]


class SalaryAggregationStates(StatesGroup):
    """
    Данные, которые записываются на основании ответа боту в телеграмме.
    Необходимы, чтобы передать соответствующие значения в модель SalaryAggregationRequest для работы с базой данных.
    """

    dt_from = State()
    dt_upto = State()
    group_type = State()
