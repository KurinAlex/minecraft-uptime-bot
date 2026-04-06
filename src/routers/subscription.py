from aiogram import Router, types
from aiogram.filters import Command
from sqlalchemy import select

from data.db import AsyncSession
from data.models import User

subscription_router = Router(name=__name__)


@subscription_router.message(Command("subscribe"))
async def subscribe_command(message: types.Message, session: AsyncSession):
    query = select(User).where(User.chat_id == message.chat.id)
    result = await session.execute(query)
    user: User = result.scalars().first()

    if not user:
        user = User(chat_id=message.chat.id)
        session.add(user)

    if user.is_subscribed:
        await message.answer("🔔 You are already subscribed.")
        return

    user.is_subscribed = True
    await session.commit()

    await message.answer("🔔 You are now subscribed to server status updates.")


@subscription_router.message(Command("unsubscribe"))
async def unsubscribe_command(message: types.Message, session: AsyncSession):
    query = select(User).where(User.chat_id == message.chat.id)
    result = await session.execute(query)
    user: User = result.scalars().first()

    if not user:
        user = User(chat_id=message.chat.id)
        session.add(user)

    if not user.is_subscribed:
        await message.answer("🔕 You are not subscribed.")
        return

    user.is_subscribed = False
    await session.commit()

    await message.answer("🔕 You are now unsubscribed from server status updates.")
