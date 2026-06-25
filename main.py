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

    print(data)

    if "channel_post" in data:
        post = data["channel_post"]

        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/setMessageReaction",
            json={
                "chat_id": post["chat"]["id"],
                "message_id": post["message_id"],
                "reaction": [
                    {
                        "type": "emoji",
                        "emoji": "❤️"
                    }
                ]
            }
        )

    return "ok"

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 10000))
    )
