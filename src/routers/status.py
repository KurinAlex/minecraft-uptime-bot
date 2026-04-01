import logging

from aiogram import Router, types
from aiogram.filters import Command

from services.mcserver import get_mc_status

logger = logging.getLogger(__name__)

status_router = Router(name=__name__)


@status_router.message(Command("status"))
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
