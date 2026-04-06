import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand

from config import Config
from data.db import Database
from middleware.data import DbSessionMiddleware
from routers import status_router, subscription_router
from services.mcserver import monitor


async def set_commands(bot: Bot):
    commands = [
        BotCommand(
            command="start",
            description="⚡ Start the bot",
        ),
        BotCommand(
            command="status",
            description="❔ Check the Minecraft server status",
        ),
        BotCommand(
            command="subscribe",
            description="🔔 Subscribe to server status updates",
        ),
        BotCommand(
            command="unsubscribe",
            description="🔕 Unsubscribe from server status updates",
        ),
    ]

    await bot.set_my_commands(commands)


async def setup_bot(bot: Bot):
    await Database.create_tables()
    await set_commands(bot)


async def main():
    logging.basicConfig(level=logging.INFO)

    dp = Dispatcher()
    dp.include_router(status_router)
    dp.include_router(subscription_router)

    dp.startup.register(setup_bot)

    dp.update.middleware.register(DbSessionMiddleware())

    bot = Bot(token=Config.bot_token())

    asyncio.create_task(monitor(bot))
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
