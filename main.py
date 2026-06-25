import requests
import asyncio
import os
from flask import Flask, request
from flask import Flask
from threading import Thread

# ===== WEBKEEP ALIVE =====
app_web = Flask(__name__)
OWNER_ID = int(os.getenv("OWNER_ID", "0"))

@app_web.route("/")
def home():
    return "Bot is online!"

def keep_alive():
    port = int(os.environ.get("PORT", 10000))
    Thread(target=lambda: app_web.run(host="0.0.0.0", port=port)).start()

BOT_TOKEN = os.getenv("BOT_TOKEN")

app = Flask(__name__)

@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    data = request.get_json()

    if "channel_post" in data:
        post = data["channel_post"]

        chat_id = post["chat"]["id"]
        message_id = post["message_id"]

        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/setMessageReaction",
            json={
                "chat_id": chat_id,
                "message_id": message_id,
                "reaction": [
                    {
                        "type": "emoji",
                        "emoji": "❤️"
                    }
                ]
            }
        )

    return "ok"

@app.route("/")
def home():
    return "Reaction Bot Running!"

if __name__ == "__main__":
    keep_alive()
    app.run(host="0.0.0.0", port=10000)
