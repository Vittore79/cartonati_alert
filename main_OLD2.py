import feedparser
import schedule
import time
import asyncio
import os

from datetime import datetime, timezone, timedelta
from telegram import Bot

# =========================
# CONFIG
# =========================

TELEGRAM_TOKEN = "8312714597:AAGXOyaW8b1k_PBS0OYf92MdgoDP2fImJXs"
CHAT_ID = "7494998558"

RSS_FEEDS = [

    # GOOGLE NEWS
    "https://news.google.com/rss/search?q=Inter+scandalo&hl=it&gl=IT&ceid=IT:it",

    "https://news.google.com/rss/search?q=Juventus+FIGC&hl=it&gl=IT&ceid=IT:it",

    "https://news.google.com/rss/search?q=Serie+A+ultras&hl=it&gl=IT&ceid=IT:it",

    "https://news.google.com/rss/search?q=Inter+inchiesta&hl=it&gl=IT&ceid=IT:it",

    "https://news.google.com/rss/search?q=Juventus+scandalo&hl=it&gl=IT&ceid=IT:it",

    # RSS DIRETTI
    "https://www.ansa.it/sito/notizie/sport/calcio/calcio_rss.xml",

    "https://www.gazzetta.it/rss/home.xml"
]

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

        already_sent = set(
            f.read().splitlines()
        )

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
    "caos",
    "accuse",
    "scontro",
    "violazione",
    "irregolarità",

    # extra
    "mercato",
    "tifosi",
    "contestazione",
    "curva",
    "società",
    "esonero",
    "dimissioni",
    "attacco",
    "denuncia",
    "inchieste",
    "guai",
    "caso"
]

team_words = [

    "inter",
    "juventus",
    "serie a",
    "milan",
    "napoli",
    "roma",
    "lazio"
]

# =========================
# HEARTBEAT
# =========================

def heartbeat():

    print("\n========================")
    print("BOT ONLINE")
    print("========================")

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
    print("Controllo news RSS...")
    print("Ora:", time.strftime("%H:%M:%S"))
    print("========================")

    sent_count = 0

    for feed_url in RSS_FEEDS:

        print(f"\nFeed: {feed_url}")

        try:

            feed = feedparser.parse(feed_url)

            print(f"Articoli trovati: {len(feed.entries)}")

            for entry in feed.entries[:20]:

                try:

                    title = entry.title
                    link = entry.link

                    # =========================
                    # DATA ARTICOLO
                    # =========================

                    if hasattr(entry, "published_parsed"):

                        article_date = datetime(
                            *entry.published_parsed[:6],
                            tzinfo=timezone.utc
                        )

                        now = datetime.now(timezone.utc)

                        age = now - article_date

                        # SOLO NEWS ULTIME 48H
                        if age > timedelta(hours=48):

                            print("Vecchia:", title)

                            continue

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

                    with open(
                        SENT_FILE,
                        "a",
                        encoding="utf-8"
                    ) as f:

                        f.write(unique_id + "\n")

                    # =========================
                    # TELEGRAM
                    # =========================

                    message = (

                        f"🚨 NUOVA NEWS\n\n"
                        f"📰 {title}\n\n"
                        f"🔗 {link}"
                    )

                    asyncio.run(

                        send_telegram_message(message)
                    )

                    sent_count += 1

                    print("Inviata:", title)

                except Exception as e:

                    print("Errore articolo:", e)

        except Exception as e:

            print("Errore feed:", e)

    print("\n========================")
    print(f"News inviate: {sent_count}")
    print("========================")

# =========================
# SCHEDULER
# =========================

schedule.every(60).minutes.do(search_news)

# heartbeat ogni 12 ore
schedule.every(12).hours.do(heartbeat)

print("\n========================")
print("BOT AVVIATO")
print("========================")

heartbeat()

search_news()

while True:

    schedule.run_pending()

    time.sleep(1)