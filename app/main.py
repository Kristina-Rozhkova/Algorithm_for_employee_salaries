import asyncio
import os

import uvicorn
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv
from fastapi import FastAPI

from app.hanblers import router
from app.routers import salaries

load_dotenv()

app = FastAPI(
    title="Salary Aggregation API",
    description="""
    API для агрегации зарплат сотрудников

    Позволяет получать данные о зарплатах за выбранный период с группировкой по:
    - часам (`hour`)
    - дням (`day`)
    - месяцам (`month`)
    """,
    version="1.0.0",
    contact={
        "name": "Рожкова Кристина",
        "email": "kristina.rozhkova.2018@list.ru",
    },
)

app.include_router(salaries.router)


async def run_bot():
    bot = Bot(token=os.getenv("TELEGRAM_BOT_TOKEN"))
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)


async def main():
    server = uvicorn.Server(
        uvicorn.Config(app=app, host="0.0.0.0", port=8000, reload=True)
    )

    await asyncio.gather(server.serve(), run_bot())


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот выключен")
