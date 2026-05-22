from telegram import Bot
import asyncio

from config import (
    TELEGRAM_TOKEN,
    CHAT_ID
)

bot = Bot(
    token=TELEGRAM_TOKEN
)

# =========================
# INVIO TELEGRAM
# =========================

async def async_send(message):

    try:

        await bot.send_message(
            chat_id=CHAT_ID,
            text=message
        )

    except Exception as e:

        print(
            "Errore Telegram:",
            e
        )

def send_message(message):

    loop = asyncio.new_event_loop()

    asyncio.set_event_loop(loop)

    loop.run_until_complete(
        async_send(message)
    )

    loop.close()