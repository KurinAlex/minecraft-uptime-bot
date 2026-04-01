import asyncio
import logging

from aiogram import Bot
from mcstatus import JavaServer
from mcstatus.responses import JavaStatusResponse

from config import Config
from services.subscription import load_subscriptions, subscription_lock

logger = logging.getLogger(__name__)

last_status: bool | None = None
last_players: set[str] = set()


async def get_mc_status() -> JavaStatusResponse | None:
    try:
        server = JavaServer.lookup(
            f"{Config.mc_server_host()}:{Config.mc_server_port()}"
        )
        status = await server.async_status()
        return status
    except Exception:
        return None


async def notify_subscribers(bot: Bot, message: str):
    async with subscription_lock:
        subscribers = load_subscriptions()
        
    if not subscribers:
        return

    for chat_id in subscribers:
        try:
            await bot.send_message(chat_id, message)
        except Exception as e:
            logger.error(f"Failed to send message to {chat_id}: {e}")


async def monitor(bot: Bot):
    global last_status
    global last_players

    while True:
        status = await get_mc_status()

        online = status is not None
        if online != last_status:
            message = "🟢 Server is back ONLINE" if online else "🔴 Server went OFFLINE"
            await notify_subscribers(bot, message)
            last_status = online

        if not online:
            last_players.clear()
        else:
            current_players = (
                set(player.name for player in status.players.sample)
                if status.players.sample
                else set()
            )

            joined_players = current_players - last_players
            for player in joined_players:
                await notify_subscribers(bot, f"🎉 {player} joined the server.")

            left_players = last_players - current_players
            for player in left_players:
                await notify_subscribers(bot, f"👋 {player} left the server.")

            last_players = current_players

        await asyncio.sleep(Config.check_interval())
