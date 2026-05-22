import feedparser
import schedule
import time

from datetime import datetime, timezone, timedelta

from config import (
    RSS_FEEDS,
    IMPORTANT_WORDS,
    TEAM_WORDS,
    YOUTUBE_WORDS
)

from feeds.youtube_sources import (
    YOUTUBE_CHANNELS
)

from modules.telegram_sender import (
    send_message
)

from modules.duplicate_manager import (
    is_duplicate,
    save_duplicate
)

# =========================
# HEARTBEAT
# =========================

def heartbeat():

    print("\n========================")
    print("BOT ONLINE")
    print("========================")

    send_message(
        "✅ Cartonati Alert online e funzionante"
    )

# =========================
# FILTRO RSS
# =========================

def is_interesting(title):

    title_lower = title.lower()

    has_important = any(
        word in title_lower
        for word in IMPORTANT_WORDS
    )

    has_team = any(
        word in title_lower
        for word in TEAM_WORDS
    )

    return has_important and has_team

# =========================
# FILTRO YOUTUBE
# =========================

def is_interesting_youtube(title):

    title_lower = title.lower()

    return any(
        word in title_lower
        for word in YOUTUBE_WORDS
    )

# =========================
# RSS NEWS
# =========================

def check_rss_feeds():

    print("\n========================")
    print("CONTROLLO RSS")
    print("========================")

    sent_count = 0

    for feed_url in RSS_FEEDS:

        print(f"\nFeed: {feed_url}")

        try:

            feed = feedparser.parse(feed_url)

            print(
                f"Articoli trovati: {len(feed.entries)}"
            )

            for entry in feed.entries[:20]:

                try:

                    title = entry.title
                    link = entry.link

                    # =========================
                    # CONTROLLO DATA
                    # =========================

                    if hasattr(
                        entry,
                        "published_parsed"
                    ):

                        article_date = datetime(
                            *entry.published_parsed[:6],
                            tzinfo=timezone.utc
                        )

                        now = datetime.now(
                            timezone.utc
                        )

                        age = now - article_date

                        # SOLO ultime 48 ore
                        if age > timedelta(hours=48):

                            print(
                                "Vecchia:",
                                title
                            )

                            continue

                    # =========================
                    # FILTRI
                    # =========================

                    if not is_interesting(title):

                        print(
                            "Scartata:",
                            title
                        )

                        continue

                    # =========================
                    # DUPLICATI
                    # =========================

                    unique_id = (
                        "rss_" +
                        title.lower().strip()
                    )

                    if is_duplicate(unique_id):

                        print(
                            "Duplicata:",
                            title
                        )

                        continue

                    save_duplicate(unique_id)

                    # =========================
                    # MESSAGGIO
                    # =========================

                    message = (

                        f"🚨 NEWS RSS\n\n"
                        f"📰 {title}\n\n"
                        f"🔗 {link}"
                    )

                    send_message(message)

                    sent_count += 1

                    print(
                        "Inviata:",
                        title
                    )

                except Exception as e:

                    print(
                        "Errore articolo:",
                        e
                    )

        except Exception as e:

            print(
                "Errore feed:",
                e
            )

    print(
        f"\nRSS inviate: {sent_count}"
    )

# =========================
# YOUTUBE
# =========================

def check_youtube_channels():

    print("\n========================")
    print("CONTROLLO YOUTUBE")
    print("========================")

    sent_count = 0

    for channel_data in YOUTUBE_CHANNELS:

        try:

            channel_name = channel_data["name"]
            channel_id = channel_data["id"]

            rss_url = (
                "https://www.youtube.com/feeds/videos.xml?channel_id="
                + channel_id
            )

            feed = feedparser.parse(rss_url)

            print(
                f"\nCanale: {channel_name}"
            )

            for entry in feed.entries[:5]:

                try:

                    title = entry.title
                    link = entry.link

                    # =========================
                    # DATA VIDEO
                    # =========================

                    if hasattr(
                        entry,
                        "published_parsed"
                    ):

                        video_date = datetime(
                            *entry.published_parsed[:6],
                            tzinfo=timezone.utc
                        )

                        now = datetime.now(
                            timezone.utc
                        )

                        age = now - video_date

                        # SOLO ultime 72 ore
                        if age > timedelta(hours=72):

                            print(
                                "Video vecchio:",
                                title
                            )

                            continue

                    # =========================
                    # FILTRO YOUTUBE
                    # =========================

                    if not is_interesting_youtube(title):

                        print(
                            "Video scartato:",
                            title
                        )

                        continue

                    # =========================
                    # DUPLICATI
                    # =========================

                    unique_id = (
                        "yt_" +
                        title.lower().strip()
                    )

                    if is_duplicate(unique_id):

                        print(
                            "Video duplicato:",
                            title
                        )

                        continue

                    save_duplicate(unique_id)

                    # =========================
                    # TELEGRAM
                    # =========================

                    message = (

                        f"🎥 NUOVO VIDEO\n\n"
                        f"📺 Canale: {channel_name}\n\n"
                        f"📰 {title}\n\n"
                        f"🔗 {link}"
                    )

                    send_message(message)

                    sent_count += 1

                    print(
                        "Video inviato:",
                        title
                    )

                except Exception as e:

                    print(
                        "Errore video:",
                        e
                    )

        except Exception as e:

            print(
                "Errore YouTube:",
                e
            )

    print(
        f"\nVideo inviati: {sent_count}"
    )

# =========================
# CONTROLLO GENERALE
# =========================

def run_all_checks():

    print("\n========================")
    print("NUOVO CONTROLLO")
    print(
        "Ora:",
        time.strftime("%H:%M:%S")
    )
    print("========================")

    check_rss_feeds()

    check_youtube_channels()

# =========================
# AVVIO
# =========================

print("\n========================")
print("CARTONATI ALERT AVVIATO")
print("========================")

heartbeat()

run_all_checks()

# ogni 60 minuti
schedule.every(60).minutes.do(
    run_all_checks
)

# heartbeat ogni 12 ore
schedule.every(12).hours.do(
    heartbeat
)

# loop infinito
while True:

    schedule.run_pending()

    time.sleep(1)