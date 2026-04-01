import asyncio
import json
import os

subscription_lock = asyncio.Lock()
SUBSCRIBERS_FILE = "subscribers.json"


def save_subscriptions(subscribers):
    with open(SUBSCRIBERS_FILE, "w") as f:
        json.dump(subscribers, f)


def load_subscriptions():
    if not os.path.exists(SUBSCRIBERS_FILE):
        save_subscriptions([])

    with open(SUBSCRIBERS_FILE) as f:
        return json.load(f)
