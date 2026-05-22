import os

SENT_FILE = "sent_news.txt"

if os.path.exists(SENT_FILE):

    with open(SENT_FILE, "r", encoding="utf-8") as f:

        already_sent = set(
            f.read().splitlines()
        )

else:

    already_sent = set()

def is_duplicate(unique_id):

    return unique_id in already_sent

def save_duplicate(unique_id):

    already_sent.add(unique_id)

    with open(
        SENT_FILE,
        "a",
        encoding="utf-8"
    ) as f:

        f.write(unique_id + "\n")