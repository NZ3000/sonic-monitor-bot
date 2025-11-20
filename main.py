import os
import time
import requests
from telegram import Bot
from telegram.error import TelegramError

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
WATCH_ADDRESS = os.getenv("WATCH_ADDRESS").lower()

bot = Bot(token=BOT_TOKEN)
last_tx = None

SCAN_API = "https://api.sonicscan.org/api"  # Sonic explorer API

def check_transactions():
    global last_tx
    try:
        params = {
            "module": "account",
            "action": "txlist",
            "address": WATCH_ADDRESS,
            "sort": "desc"
        }
        r = requests.get(SCAN_API, params=params).json()

        if r["status"] != "1":
            return

        tx = r["result"][0]
        tx_hash = tx["hash"]

        if last_tx is None:
            last_tx = tx_hash
            return

        if tx_hash != last_tx:
            last_tx = tx_hash
            msg = (
                f"Нова транзакція\n"
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
