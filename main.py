import os
import requests
from flask import Flask, request

BOT_TOKEN = os.getenv("BOT_TOKEN")

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot Running"

@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    data = request.get_json()

    print("UPDATE:", data)

    if "channel_post" in data:
        post = data["channel_post"]

        payload = {
            "chat_id": post["chat"]["id"],
            "message_id": post["message_id"],
            "reaction": [
                {
                    "type": "emoji",
                    "emoji": "❤️"
                },
                {
                    "type": "emoji",
                    "emoji": "🔥"
                }
            ]
        }

        r = requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/setMessageReaction",
            json=payload
        )

        print("STATUS:", r.status_code)
        print("RESPONSE:", r.text)

    return "ok"

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 10000))
    )
