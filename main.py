import requests
import schedule
import time
import asyncio
import os
from telegram import Bot

# =========================
# CONFIG
# =========================

TELEGRAM_TOKEN = "8312714597:AAGXOyaW8b1k_PBS0OYf92MdgoDP2fImJXs"
CHAT_ID = "7494998558"
NEWS_API_KEY = "66c39f4197af4b1eb102c8308528daa1"

SEARCH_QUERY = (
    '("Inter" OR "Juventus" OR "Serie A" OR "Tether Juve") '
    'AND ("inchiesta" OR "scandalo" OR "indagini" OR "polemiche" '
    'OR "calcioscommesse" OR "procura" OR "ardoino")'
)

bot = Bot(token=TELEGRAM_TOKEN)

SENT_FILE = "sent_news.txt"

if os.path.exists(SENT_FILE):
    with open(SENT_FILE, "r", encoding="utf-8") as f:
        already_sent = set(f.read().splitlines())
else:
    already_sent = set()

# =========================
# INVIO TELEGRAM
# =========================

import asyncio

async def send_telegram_message(message):
    await bot.send_message(chat_id=CHAT_ID, text=message)

# =========================
# CERCA NEWS
# =========================

def search_news():

    print("Controllo news...")

    for keyword in [SEARCH_QUERY]:

        url = (
            f"https://newsapi.org/v2/everything?"
            f"q={keyword}&"
            f"language=it&"
            f"sortBy=publishedAt&"
            f"apiKey={NEWS_API_KEY}"
        )

        response = requests.get(url)

        if response.status_code != 200:
            print("Errore API:", response.text)
            continue

        data = response.json()

        articles = data.get("articles", [])

        for article in articles[:5]:

            title = article["title"]
            link = article["url"]
            source = article["source"]["name"]

            unique_id = title.lower()

            if unique_id in already_sent:
                continue

            with open(SENT_FILE, "a", encoding="utf-8") as f:
                f.write(unique_id + "\n")

            message = (
                f"🚨 NUOVA NEWS\n\n"
                f"🔎 Keyword: {keyword}\n\n"
                f"📰 {title}\n\n"
                f"📌 Fonte: {source}\n\n"
                f"🔗 {link}"
            )

            asyncio.run(send_telegram_message(message))

            print("Inviata:", title)

# =========================
# SCHEDULER
# =========================

schedule.every(5).minutes.do(search_news)

print("BOT AVVIATO")

search_news()

while True:
    schedule.run_pending()
    time.sleep(1)