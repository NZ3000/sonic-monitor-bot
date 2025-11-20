import os
import time
import requests
from telegram import Bot
from telegram.error import TelegramError

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# Список адрес через кому у Render
WATCH_ADDRESSES = [
    addr.strip().lower()
    for addr in os.getenv("WATCH_ADDRESSES", "").split(",")
    if addr.strip()
]

bot = Bot(token=BOT_TOKEN)

# Запамʼятовуємо останні транзакції по кожній адресі
last_tx = {addr: None for addr in WATCH_ADDRESSES}

SCAN_API = "https://api.sonicscan.org/api"


def check_transactions():
    global last_tx

    for address in WATCH_ADDRESSES:
        try:
            params = {
                "module": "account",
                "action": "txlist",
                "address": address,
                "sort": "desc"
            }

            r = requests.get(SCAN_API, params=params).json()

            if r["status"] != "1":
                continue

            tx = r["result"][0]
            tx_hash = tx["hash"]

            # перший запуск
            if last_tx[address] is None:
                last_tx[address] = tx_hash
                continue

            # нова транзакція
            if tx_hash != last_tx[address]:
                last_tx[address] = tx_hash

                msg = (
                    f"Нова транзакція для {address}\n"
                    f"Hash: {tx_hash}\n"
                    f"From: {tx['from']}\n"
                    f"To: {tx['to']}\n"
                    f"Value: {tx['value']}"
                )

                bot.send_message(chat_id=CHAT_ID, text=msg)

        except TelegramError as e:
            print("Telegram error:", e)
        except Exception as e:
            print("Error:", e)


if __name__ == "__main__":
    print("Bot started")
    while True:
        check_transactions()
        time.sleep(8)
