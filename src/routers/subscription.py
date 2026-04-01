from aiogram import Router, types
from aiogram.filters import Command

from services.subscription import (
    load_subscriptions,
    save_subscriptions,
    subscription_lock,
)

subscription_router = Router(name=__name__)


@subscription_router.message(Command("subscribe"))
async def subscribe_command(message: types.Message):
    async with subscription_lock:
        subscribers = load_subscriptions()
        if message.chat.id in subscribers:
            await message.answer("🔔 You are already subscribed.")
            return

        subscribers.append(message.chat.id)
        save_subscriptions(subscribers)

    await message.answer("🔔 You are now subscribed to server status updates.")


@subscription_router.message(Command("unsubscribe"))
async def unsubscribe_command(message: types.Message):
    async with subscription_lock:
        subscribers = load_subscriptions()
        if message.chat.id not in subscribers:
            await message.answer("🔕 You are not subscribed.")
            return

        subscribers.remove(message.chat.id)
        save_subscriptions(subscribers)

    await message.answer("🔕 You are now unsubscribed from server status updates.")
