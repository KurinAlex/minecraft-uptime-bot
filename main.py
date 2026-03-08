import asyncio
import json
import logging

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from mcstatus import JavaServer

from config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_mc_status():
    server = JavaServer.lookup(f"{Config.mc_server_host()}:{Config.mc_server_port()}")
    status = server.status()
    return status


subscription_lock = asyncio.Lock()
dp = Dispatcher()


@dp.message(Command("status"))
async def status_command(message: types.Message):
    try:
        status = get_mc_status()
        text = "🟢 Server is ONLINE\n\n"
        if status.players.online == 0:
            text += "No players are currently online."
        elif status.players.sample:
            players = "\n".join(f"- {player.name}" for player in status.players.sample)
            text += f"Now playing:\n{players}"
        else:
            text += f"{status.players.online} player(s) are currently online."
    except Exception:
        text = "🔴 Server is OFFLINE"

    await message.answer(text)


@dp.message(Command("subscribe"))
async def subscribe_command(message: types.Message):
    async with subscription_lock:
        with open("subscriptions.json") as f:
            subscribers = json.load(f)

        if message.chat.id in subscribers:
            await message.answer("🔔 You are already subscribed.")
            return

        subscribers.append(message.chat.id)
        with open("subscriptions.json", "w") as f:
            json.dump(subscribers, f)

        await message.answer("🔔 You are now subscribed to server status updates.")


@dp.message(Command("unsubscribe"))
async def unsubscribe_command(message: types.Message):
    async with subscription_lock:
        with open("subscriptions.json") as f:
            subscribers = json.load(f)

        if message.chat.id not in subscribers:
            await message.answer("🔕 You are not subscribed.")
            return

        subscribers.remove(message.chat.id)
        with open("subscriptions.json", "w") as f:
            json.dump(subscribers, f)

        await message.answer("🔕 You are now unsubscribed from server status updates.")


async def main():
    bot_token = Config.bot_token()
    bot = Bot(token=bot_token)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
