from datetime import datetime
from unittest.mock import AsyncMock, patch

import pytest

import app.keyboards as kb
from app import handlers
from app.models import SalaryAggregationRequest, SalaryAggregationStates


@pytest.mark.asyncio
async def test_start_command(message):
    """ Тестирование вывода приветственного сообщения """
    await handlers.cmd_start(message)
    message.answer.assert_called_with("Привет!\nКакую информацию нужно подготовить сегодня?", reply_markup=kb.main)


@pytest.mark.asyncio
async def test_cmd_help(message):
    """ Тестирование вывода сообщения с подсказкой """
    await handlers.cmd_help(message)
    message.answer.assert_called_with("Чтобы продолжить, выберите пункт меню")


@pytest.mark.asyncio
async def test_salary_information(message):
    """ Тестирование вывода приглашения для выбора типа группировки """
    await handlers.salary_information(message)
    message.answer.assert_called_with("Выберите тип группировки выплат", reply_markup=kb.group_type)


@pytest.mark.asyncio
async def test_handle_group_type(callback, state):
    """ Тестирование выбора типа группировки выплат """
    callback.data = "month"

    await handlers.handle_group_type(callback, state)

    state.set_state.assert_called_with(SalaryAggregationStates.dt_from)
    callback.message.answer.assert_called_with(
        "Введите начало периода в формате 2022-09-01T00:00:00"
    )
    callback.answer.assert_called_once()


@pytest.mark.asyncio
async def test_aggregation_dt_from(message, state):
    """ Тестирование ручки получения начальной даты от пользователя """
    message.text = "2022-09-01T00:00:00"

    await handlers.aggregation_dt_from(message, state)

    state.update_data.assert_called_once_with(dt_from="2022-09-01T00:00:00")
    state.set_state.assert_called_once_with(SalaryAggregationStates.dt_upto)
    message.answer.assert_called_once_with(
        "Введите конец периода в формате 2022-09-01T00:00:00"
    )


@pytest.mark.asyncio
async def test_aggregation_dt_from_missing_time(message, state):
    """ Проверка выброса ошибки при вводе даты без времени """
    message.text = "2022-09-01"

    await handlers.aggregation_dt_from(message, state)

    state.update_data.assert_not_called()
    message.answer.assert_called_with(
        "Неверный формат даты. Ожидается: ГГГГ-MM-ДДTЧЧ:MM:СС. Ошибка: Требуется полный формат с указанием времени"
    )


@pytest.mark.asyncio
async def test_aggregation_dt_from_invalid_format(message, state):
    """ Проверка выброса ошибки в случае невалидного формата даты """
    invalid_formats = [
        "2022/09/01T00:00:00",
        "01-09-2022T00:00:00",
        "2022-09-01 00:00:00",
        "2022-09-01T25:00:00"
    ]

    for invalid in invalid_formats:
        message.text = invalid

        await handlers.aggregation_dt_from(message, state)

        state.update_data.assert_not_called()
        assert "Неверный формат даты" in message.answer.call_args[0][0]


@pytest.mark.asyncio
async def test_aggregation_dt_upto(message, state):
    """ Проверка вывода информации по агрегации данных """
    message.text = "2022-11-01T00:00:00"

    state.get_data.return_value = {
        "dt_from": "2022-09-01T00:00:00",
        "dt_upto": "2022-11-01T00:00:00",
        "group_type": "month"
    }

    with patch('app.handlers.aggregate_salary', new=AsyncMock()) as mock_agg:
        mock_agg.return_value = {
            "dataset": [100, 200, 300],
            "labels": ["2022-09-01T00:00:00", "2022-10-01T00:00:00", "2022-11-01T00:00:00"]
        }

        await handlers.aggregation_dt_upto(message, state)

        mock_agg.assert_awaited_once_with(
            SalaryAggregationRequest(
                dt_from=datetime.fromisoformat("2022-09-01T00:00:00"),
                dt_upto=datetime.fromisoformat("2022-11-01T00:00:00"),
                group_type="month"
            )
        )

        message.answer.assert_called_once_with(
            "Данные: [100, 200, 300]\nМетки: ['2022-09-01T00:00:00', '2022-10-01T00:00:00', '2022-11-01T00:00:00']"
        )


@pytest.mark.asyncio
async def test_aggregation_dt_upto_before_dt_from(message, state):
    """ Проверка случая, когда конечная дата раньше начальной """
    message.text = "2022-08-31T23:59:00"

    state.get_data.return_value = {
        "dt_from": "2022-09-01T00:00:00",
        "group_type": "month"
    }

    await handlers.aggregation_dt_upto(message, state)

    message.answer.assert_called_with(
        "Конечная дата должна быть позже начальной"
    )


@pytest.mark.asyncio
async def test_aggregation_dt_upto_same_as_from(message, state):
    """ Проверка случая, когда даты одинаковые """
    message.text = "2022-09-01T00:00:00"

    state.get_data.return_value = {
        "dt_from": "2022-09-01T00:00:00",
        "group_type": "month"
    }

    await handlers.aggregation_dt_upto(message, state)

    message.answer.assert_called_with(
        "Конечная дата должна быть позже начальной"
    )
