import asyncio
import json
import logging
import os

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import BotCommand
from mcstatus import JavaServer
from mcstatus.responses import JavaStatusResponse

from config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def get_mc_status() -> JavaStatusResponse | None:
    try:
        server = JavaServer.lookup(
            f"{Config.mc_server_host()}:{Config.mc_server_port()}"
        )
        status = await server.async_status()
        return status
    except Exception:
        return None


subscription_lock = asyncio.Lock()
dp = Dispatcher()


@dp.message(Command("status"))
async def status_command(message: types.Message):
    status = await get_mc_status()
    if not status:
        text = "🔴 Server is OFFLINE"
        await message.answer(text)
        return

    text = "🟢 Server is ONLINE\n\n"
    if status.players.online == 0:
        text += "No players are currently online."
    elif status.players.sample:
        players = "\n".join(f"- {player.name}" for player in status.players.sample)
        text += f"Now playing:\n{players}"
    else:
        text += f"{status.players.online} player(s) are currently online."

    await message.answer(text)


SUBSCRIBERS_FILE = "subscribers.json"


def load_subscriptions():
    if not os.path.exists(SUBSCRIBERS_FILE):
        save_subscriptions([])

    with open(SUBSCRIBERS_FILE) as f:
        return json.load(f)


def save_subscriptions(subscribers):
    with open(SUBSCRIBERS_FILE, "w") as f:
        json.dump(subscribers, f)


@dp.message(Command("subscribe"))
async def subscribe_command(message: types.Message):
    async with subscription_lock:
        subscribers = load_subscriptions()
        if message.chat.id in subscribers:
            await message.answer("🔔 You are already subscribed.")
            return

        subscribers.append(message.chat.id)
        save_subscriptions(subscribers)

        await message.answer("🔔 You are now subscribed to server status updates.")


@dp.message(Command("unsubscribe"))
async def unsubscribe_command(message: types.Message):
    async with subscription_lock:
        subscribers = load_subscriptions()
        if message.chat.id not in subscribers:
            await message.answer("🔕 You are not subscribed.")
            return

        subscribers.remove(message.chat.id)
        save_subscriptions(subscribers)

        await message.answer("🔕 You are now unsubscribed from server status updates.")


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


async def notify_subscribers(bot: Bot, online: bool):
    subscribers = load_subscriptions()
    if not subscribers:
        return

    message = (
        "🟢 Minecraft server is back ONLINE"
        if online
        else "🔴 Minecraft server went OFFLINE"
    )

    for chat_id in subscribers:
        try:
            await bot.send_message(chat_id, message)
        except Exception as e:
            logger.error(f"Failed to send message to {chat_id}: {e}")


async def monitor(bot: Bot):
    global last_status

    while True:
        status = await get_mc_status()
        online = status is not None

        if last_status is None:
            last_status = online

        if online != last_status:
            await notify_subscribers(bot, online)

        last_status = online

        await asyncio.sleep(Config.check_interval())


async def main():
    bot_token = Config.bot_token()
    bot = Bot(token=bot_token)
    await set_default_commands(bot)

    asyncio.create_task(monitor(bot))
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
