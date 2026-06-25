import os
import time
import threading
import requests
from flask import Flask, request

# Basahin ang magkakadugtong na tokens mula sa Render (comma-separated)
BOT_TOKENS_STR = os.getenv("BOT_TOKENS", "")
BOT_TOKENS = [token.strip() for token in BOT_TOKENS_STR.split(",") if token.strip()]

app = Flask(__name__)

# CONFIGURATION: Iba't ibang emoji at delay para sa bawat Bot (Bot 1 to Bot 5)
# Index 0 = Bot 1, Index 1 = Bot 2, atbp.
BOT_CONFIGS = [
    {"emoji": "❤️", "delay": 0},  # Bot 1: Agad-agad (0 seconds delay)
    {"emoji": "👍", "delay": 2},  # Bot 2: Pagkatapos ng 2 seconds
    {"entry": "🔥", "emoji": "🔥", "delay": 4},  # Bot 3: Pagkatapos ng 4 seconds
    {"emoji": "🥰", "delay": 6},  # Bot 4: Pagkatapos ng 6 seconds
    {"emoji": "🎉", "delay": 8}   # Bot 5: Pagkatapos ng 8 seconds
]

@app.route("/")
def home():
    return f"Bot Farm Running. Loaded Bots: {len(BOT_TOKENS)}", 200

# Ito ang function na nagpapatakbo ng delay bago mag-react ang bot
def delayed_reaction(token, chat_id, message_id, emoji, delay_seconds):
    if delay_seconds > 0:
        time.sleep(delay_seconds) # Hihintay muna dito bago ituloy
        
    url = f"https://api.telegram.org/bot{token}/setMessageReaction"
    payload = {
        "chat_id": chat_id,
        "message_id": message_id,
        "reaction": [{"type": "emoji", "emoji": emoji}]
    }
    try:
        response = requests.post(url, json=payload, timeout=5)
        print(f"Bot {token[:10]}... reacted {emoji} status: {response.status_code}")
    except Exception as e:
        print(f"Error sa bot {token[:10]}... : {e}")

# Function para gawan ng kanya-kanyang webhook route ang mga bots
def setup_routes():
    for index, token in enumerate(BOT_TOKENS):
        endpoint_name = f"webhook_{token[:10]}_{index}"
        
        # Kunin ang nakalaang emoji at delay para sa bot na ito (or gamitin ang default kung sumobra sa 5 bots)
        config = BOT_CONFIGS[index] if index < len(BOT_CONFIGS) else {"emoji": "❤️", "delay": 0}

        def create_webhook_handler(bot_token=token, bot_config=config):
            def handler():
                data = request.get_json(silent=True)
                if data and "channel_post" in data:
                    post = data["channel_post"]
                    chat_id = post["chat"]["id"]
                    message_id = post["message_id"]

                    # Tumatakbo ito sa background gamit ang Threading para magawa ang delay
                    threading.Thread(
                        target=delayed_reaction,
                        args=(bot_token, chat_id, message_id, bot_config["emoji"], bot_config["delay"])
                    ).start()

                return "ok", 200
            return handler

        # I-register ang ruta (e.g., /token1, /token2)
        app.add_url_rule(
            f"/{token}",
            endpoint=endpoint_name,
            view_func=create_webhook_handler(),
            methods=["POST"]
        )

setup_routes()

if __name__ == "__main__":
    if not BOT_TOKENS:
        print("WARNING: Walang bot tokens na nakalagay sa BOT_TOKENS environment variable!")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
