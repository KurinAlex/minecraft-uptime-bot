import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand

from config import Config
from routers import status_router, subscription_router
from services.mcserver import monitor


async def set_default_commands(bot: Bot):
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


async def main():
    logging.basicConfig(level=logging.INFO)

    bot = Bot(token=Config.bot_token())
    await set_default_commands(bot)

    dp = Dispatcher()
    dp.include_router(status_router)
    dp.include_router(subscription_router)

    asyncio.create_task(monitor(bot))
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
