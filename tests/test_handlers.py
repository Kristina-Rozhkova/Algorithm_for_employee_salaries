from datetime import datetime
from unittest.mock import AsyncMock, patch

import pytest
from aiogram import types
from aiogram.fsm.context import FSMContext

import app.keyboards as kb
from app import handlers
from app.models import SalaryAggregationRequest, SalaryAggregationStates


@pytest.mark.asyncio
async def test_start_command():
    """ Тестирование вывода приветственного сообщения """
    message = AsyncMock(spec=types.Message)
    message.answer = AsyncMock()

    await handlers.cmd_start(message)
    message.answer.assert_called_with("Привет!\nКакую информацию нужно подготовить сегодня?", reply_markup=kb.main)


@pytest.mark.asyncio
async def test_cmd_help():
    """ Тестирование вывода сообщения с подсказкой """
    message = AsyncMock(spec=types.Message)
    message.answer = AsyncMock()

    await handlers.cmd_help(message)
    message.answer.assert_called_with("Чтобы продолжить, выберите пункт меню")


@pytest.mark.asyncio
async def test_salary_information():
    """ Тестирование вывода приглашения для выбора типа группировки """
    message = AsyncMock(spec=types.Message)
    message.answer = AsyncMock()

    await handlers.salary_information(message)
    message.answer.assert_called_with("Выберите тип группировки выплат", reply_markup=kb.group_type)


@pytest.mark.asyncio
async def test_handle_group_type():
    """ Тестирование выбора типа группировки выплат """
    callback = AsyncMock(spec=types.CallbackQuery)
    callback.data = "month"
    callback.message = AsyncMock()
    callback.message.answer = AsyncMock()
    callback.answer = AsyncMock()

    state = AsyncMock(spec=FSMContext)

    await handlers.handle_group_type(callback, state)

    state.set_state.assert_called_with(SalaryAggregationStates.dt_from)
    callback.message.answer.assert_called_with(
        "Введите начало периода в формате 2022-09-01T00:00:00"
    )


@pytest.mark.asyncio
async def test_aggregation_dt_from():
    """ Тестирование ручки получения начальной даты от пользователя """
    message = AsyncMock(spec=types.Message)
    message.text = "2022-09-01T00:00:00"
    message.answer = AsyncMock()

    state = AsyncMock(spec=FSMContext)
    state.update_data = AsyncMock()
    state.set_state = AsyncMock()

    await handlers.aggregation_dt_from(message, state)

    state.update_data.assert_called_once_with(dt_from="2022-09-01T00:00:00")
    state.set_state.assert_called_once_with(SalaryAggregationStates.dt_upto)
    message.answer.assert_called_once_with(
        "Введите конец периода в формате 2022-09-01T00:00:00"
    )


@pytest.mark.asyncio
async def test_aggregation_dt_from_missing_time():
    """ Проверка выброса ошибки при вводе даты без времени """
    message = AsyncMock(text="2022-09-01")
    message.answer = AsyncMock()
    state = AsyncMock()

    await handlers.aggregation_dt_from(message, state)

    state.update_data.assert_not_called()
    message.answer.assert_called_with(
        "Неверный формат даты. Ожидается: ГГГГ-MM-ДДTЧЧ:MM:СС. Ошибка: Требуется полный формат с указанием времени"
    )


@pytest.mark.asyncio
async def test_aggregation_dt_from_invalid_format():
    """ Проверка выброса ошибки в случае невалидного формата даты """
    invalid_formats = [
        "2022/09/01T00:00:00",
        "01-09-2022T00:00:00",
        "2022-09-01 00:00:00",
        "2022-09-01T25:00:00"
    ]

    for invalid in invalid_formats:
        message = AsyncMock(text=invalid)
        message.answer = AsyncMock()
        state = AsyncMock()

        await handlers.aggregation_dt_from(message, state)

        state.update_data.assert_not_called()
        assert "Неверный формат даты" in message.answer.call_args[0][0]


@pytest.mark.asyncio
async def test_aggregation_dt_upto():
    """ Проверка вывода информации по агрегации данных """
    message = AsyncMock()
    message.text = "2022-11-01T00:00:00"
    message.answer = AsyncMock()

    state = AsyncMock()
    state.get_data = AsyncMock(return_value={
        "dt_from": "2022-09-01T00:00:00",
        "dt_upto": "2022-11-01T00:00:00",
        "group_type": "month"
    })

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
async def test_aggregation_dt_upto_before_dt_from():
    """ Проверка случая, когда конечная дата раньше начальной """
    message = AsyncMock(text="2022-08-31T23:59:00")
    message.answer = AsyncMock()

    state = AsyncMock()
    state.get_data = AsyncMock(return_value={
        "dt_from": "2022-09-01T00:00:00",
        "group_type": "month"
    })

    await handlers.aggregation_dt_upto(message, state)

    message.answer.assert_called_with(
        "Конечная дата должна быть позже начальной"
    )


@pytest.mark.asyncio
async def test_aggregation_dt_upto_same_as_from():
    """ Проверка случая, когда даты одинаковые """
    message = AsyncMock(text="2022-09-01T00:00:00")
    message.answer = AsyncMock()

    state = AsyncMock()
    state.get_data = AsyncMock(return_value={
        "dt_from": "2022-09-01T00:00:00",
        "group_type": "month"
    })

    await handlers.aggregation_dt_upto(message, state)

    message.answer.assert_called_with(
        "Конечная дата должна быть позже начальной"
    )
