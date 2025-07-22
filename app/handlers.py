from datetime import datetime

from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

import app.keyboards as kb
from app.models import SalaryAggregationRequest, SalaryAggregationStates
from app.routers.salaries import aggregate_salary
from app.validators import date_difference_check, validate_iso_datetime

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(
        "Привет!\nКакую информацию нужно подготовить сегодня?", reply_markup=kb.main
    )


@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer("Чтобы продолжить, выберите пункт меню")


@router.message(F.text == "Информация о зарплате")
async def salary_information(message: Message):
    await message.answer("Выберите тип группировки выплат", reply_markup=kb.group_type)


@router.callback_query(F.data.in_(["month", "day", "hour"]))
async def handle_group_type(callback: CallbackQuery, state: FSMContext):
    group_type = callback.data
    await state.update_data(group_type=group_type)
    await state.set_state(SalaryAggregationStates.dt_from)
    await callback.message.answer(
        "Введите начало периода в формате 2022-09-01T00:00:00"
    )
    await callback.answer()


@router.message(SalaryAggregationStates.dt_from)
async def aggregation_dt_from(message: Message, state: FSMContext):
    try:
        validate_iso_datetime(message.text)

        await state.update_data(dt_from=message.text)
        await state.set_state(SalaryAggregationStates.dt_upto)
        await message.answer("Введите конец периода в формате 2022-09-01T00:00:00")

    except ValueError as e:
        await message.answer(str(e))


@router.message(SalaryAggregationStates.dt_upto)
async def aggregation_dt_upto(message: Message, state: FSMContext):
    try:
        await state.update_data(dt_upto=message.text)
        data = await state.get_data()
        validate_iso_datetime(message.text)

        dt_from = datetime.fromisoformat(data["dt_from"])
        dt_upto = datetime.fromisoformat(message.text)

        if not date_difference_check(dt_from, dt_upto):
            raise ValueError("Конечная дата должна быть позже начальной")

        request = SalaryAggregationRequest(
            dt_from=datetime.fromisoformat(data["dt_from"]),
            dt_upto=datetime.fromisoformat(data["dt_upto"]),
            group_type=data["group_type"],
        )
        result = await aggregate_salary(request)
        await message.answer(f'Данные: {result["dataset"]}\nМетки: {result["labels"]}')
    except ValueError as e:
        await message.answer(str(e))
