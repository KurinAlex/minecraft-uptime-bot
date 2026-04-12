import json
import logging

from aiogram import Router, types
from aiogram.filters import Command

from data.db import AsyncSession
from services.mcserver import get_server_data

logger = logging.getLogger(__name__)

status_router = Router(name=__name__)


@status_router.message(Command("status"))
async def status_command(message: types.Message, session: AsyncSession):
    status: bool | None = None
    last_status_data = await get_server_data(session, "status")
    if last_status_data:
        status = last_status_data.value == "online"

    players: list[str] = []
    last_players_data = await get_server_data(session, "players")
    if last_players_data:
        players = json.loads(last_players_data.value)

    if not status:
        text = "🔴 Server is OFFLINE"
        await message.answer(text)
        return

    text = "🟢 Server is ONLINE\n\n"
    if players:
        players_str = "\n".join(f"- {player}" for player in players)
        text += f"Now playing:\n{players_str}"
    else:
        text += "No players are currently online."

    await message.answer(text)
