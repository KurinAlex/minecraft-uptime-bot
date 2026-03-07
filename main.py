import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from mcstatus import JavaServer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_env_variable(name: str) -> str:
    """Retrieve required environment variable or raise error."""
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Environment variable '{name}' is required.")
    return value


server_host = get_env_variable("MC_SERVER_HOST")
server_port = int(get_env_variable("MC_SERVER_PORT"))


def check_minecraft():
    try:
        server = JavaServer.lookup(f"{server_host}:{server_port}")
        server.status()
        return True
    except Exception:
        return False


dp = Dispatcher()


@dp.message(Command("status"))
async def status_command(message: types.Message):
    online = check_minecraft()
    text = "🟢 Server is ONLINE" if online else "🔴 Server is OFFLINE"
    await message.answer(text)


async def main():
    bot_token = get_env_variable("BOT_TOKEN")
    bot = Bot(token=bot_token)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
