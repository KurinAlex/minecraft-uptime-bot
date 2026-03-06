import asyncio
import os

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from mcstatus import JavaServer

bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher()

last_status = None


def check_minecraft():
    try:
        server = JavaServer.lookup("localhost:25565")
        server.status()
        return True
    except:
        return False


@dp.message(Command("status"))
async def status_command(message: types.Message):
    online = check_minecraft()

    if online:
        await message.answer("🟢 Server ONLINE")
    else:
        await message.answer("🔴 Server OFFLINE")


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
