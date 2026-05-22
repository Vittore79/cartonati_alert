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
    'AND ("inchiesta" OR "scandalo" OR "indagini" '
    'OR "polemiche" OR "calcioscommesse" '
    'OR "procura" OR "ardoino")'
)

# =========================
# TELEGRAM
# =========================

bot = Bot(token=TELEGRAM_TOKEN)

async def send_telegram_message(message):
    try:
        await bot.send_message(
            chat_id=CHAT_ID,
            text=message
        )
    except Exception as e:
        print("Errore Telegram:", e)

# =========================
# FILE DUPLICATI
# =========================

SENT_FILE = "sent_news.txt"

if os.path.exists(SENT_FILE):
    with open(SENT_FILE, "r", encoding="utf-8") as f:
        already_sent = set(f.read().splitlines())
else:
    already_sent = set()

# =========================
# FILTRI
# =========================

important_words = [
    "inchiesta",
    "scandalo",
    "indagine",
    "procura",
    "ultras",
    "calcioscommesse",
    "figc",
    "corona",
    "tether",
    "ardoino",
    "polemica",
    "accuse",
    "caos",
    "scontro"
]

team_words = [
    "inter",
    "juventus",
    "serie a"
]

# =========================
# HEARTBEAT
# =========================

def heartbeat():
    print("Bot online e funzionante")

    asyncio.run(
        send_telegram_message(
            "✅ Cartonati Alert online e funzionante"
        )
    )

# =========================
# CERCA NEWS
# =========================

def search_news():

    print("\n========================")
    print("Controllo news...")
    print("Ora:", time.strftime("%H:%M:%S"))
    print("========================")

    url = (
        f"https://newsapi.org/v2/everything?"
        f"q={SEARCH_QUERY}&"
        f"language=it&"
        f"sortBy=publishedAt&"
        f"pageSize=20&"
        f"apiKey={NEWS_API_KEY}"
    )

    try:
        response = requests.get(url)

        if response.status_code != 200:
            print("Errore API:", response.text)
            return

        data = response.json()

        articles = data.get("articles", [])

        print(f"News trovate: {len(articles)}")

        sent_count = 0

        for article in articles:

            title = article.get("title", "")
            link = article.get("url", "")
            source = article.get("source", {}).get("name", "")

            title_lower = title.lower()

            # =========================
            # FILTRO INTELLIGENTE
            # =========================

            has_important = any(
                word in title_lower
                for word in important_words
            )

            has_team = any(
                word in title_lower
                for word in team_words
            )

            if not (has_important and has_team):
                print("Scartata:", title)
                continue

            # =========================
            # ANTI DUPLICATI
            # =========================

            unique_id = title_lower.strip()

            if unique_id in already_sent:
                print("Duplicata:", title)
                continue

            already_sent.add(unique_id)

            with open(SENT_FILE, "a", encoding="utf-8") as f:
                f.write(unique_id + "\n")

            # =========================
            # MESSAGGIO TELEGRAM
            # =========================

            message = (
                f"🚨 NUOVA NEWS\n\n"
                f"📰 {title}\n\n"
                f"📌 Fonte: {source}\n\n"
                f"🔗 {link}"
            )

            asyncio.run(
                send_telegram_message(message)
            )

            sent_count += 1

            print("Inviata:", title)

        print(f"\nNews inviate: {sent_count}")

    except Exception as e:
        print("Errore generale:", e)

# =========================
# SCHEDULER
# =========================

schedule.every(60).minutes.do(search_news)

# heartbeat ogni 12 ore
schedule.every(12).hours.do(heartbeat)

print("BOT AVVIATO")

heartbeat()
search_news()

while True:
    schedule.run_pending()
    time.sleep(1)