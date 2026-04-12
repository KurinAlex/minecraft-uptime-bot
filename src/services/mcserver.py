import asyncio
import json
import logging
from collections import Counter

from aiogram import Bot
from mcstatus import JavaServer
from mcstatus.responses import JavaStatusResponse
from sqlalchemy import select

from config import Config
from data.db import AsyncSession, Database
from data.models import ServerData, User

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


async def notify_subscribers(bot: Bot, message: str):
    async with Database.async_session() as session:
        query = select(User).where(User.is_subscribed)
        result = await session.execute(query)
        subscribed_users = result.scalars().all()

    for user in subscribed_users:
        try:
            await bot.send_message(user.chat_id, message)
        except Exception as e:
            logger.exception(f"Failed to send message to {user.chat_id}: {e}")


async def get_server_data(session: AsyncSession, key: str) -> ServerData | None:
    query = select(ServerData).where(ServerData.key == key)
    result = await session.execute(query)
    data = result.scalar()
    return data


async def upsert_server_data(
    session: AsyncSession, data: ServerData | None, key: str, value: str
) -> None:
    if data:
        data.value = value
    else:
        data = ServerData(key=key, value=value)
        session.add(data)


def sequence_difference[T](list1: list[T], list2: list[T]) -> list[T]:
    return list((Counter(list1) - Counter(list2)).elements())


async def monitor(bot: Bot):
    while True:
        # Get current server status
        status = await get_mc_status()
        current_status = status is not None
        current_players = (
            [player.name for player in status.players.sample]
            if status and status.players.sample
            else []
        )

        async with Database.async_session() as session:
            # Read last server status
            last_status: bool | None = None
            last_status_data = await get_server_data(session, "status")
            if last_status_data:
                last_status = last_status_data.value == "online"

            # Read last server players
            last_players: list[str] = []
            last_players_data = await get_server_data(session, "players")
            if last_players_data:
                last_players = json.loads(last_players_data.value)

            await upsert_server_data(
                session,
                last_status_data,
                "status",
                "online" if current_status else "offline",
            )

            await upsert_server_data(
                session,
                last_players_data,
                "players",
                json.dumps(current_players),
            )

            await session.commit()

        if current_status != last_status:
            message = (
                "🟢 Server is back ONLINE"
                if current_status
                else "🔴 Server went OFFLINE"
            )
            await notify_subscribers(bot, message)

        if current_status:
            joined_players = sequence_difference(current_players, last_players)
            for player in joined_players:
                await notify_subscribers(bot, f"🎉 {player} joined the server.")

            left_players = sequence_difference(last_players, current_players)
            for player in left_players:
                await notify_subscribers(bot, f"👋 {player} left the server.")

        await asyncio.sleep(Config.check_interval())
