import os
import time
import threading
import requests
from flask import Flask, request

# Basahin ang magkakadugtong na tokens mula sa Render (comma-separated)
BOT_TOKENS_STR = os.getenv("BOT_TOKENS", "")
BOT_TOKENS = [token.strip() for token in BOT_TOKENS_STR.split(",") if token.strip()]

app = Flask(__name__)

# CONFIGURATION: Dito natin itatakda kung anong emoji ang gagamitin base sa Keyword
# Kapag nakita ang salita sa kaliwa, ito ang ire-react ng Bot 1 hanggang Bot 5 (may kanya-kanya pa ring delay)
KEYWORD_MAPPING = {
    "sad": ["😢", "😭", "😥", "😭", "😭"],       # Kung may "sad", iyak/malungkot ang reactions
    "solid": ["🎉", "🥰", "👏", "🔥", "❤️"],     # Kung may "happy", masaya/buhay ang reactions
    "lol": ["😁", "😁", "🙉", "😁", "👍"],      # Kung may "joke", tawa ang reactions
    "paldo": ["😱", "🔥", "🔥", "🤩", "🎉"]        # Kung may "wow", gulat/bilib ang reactions
}

# DEFAULT EMOJIS: Kung walang keyword na tumama sa post mo, ito ang gagamitin (tulad ng dati)
DEFAULT_CONFIGS = [
    {"emoji": "❤️", "delay": 0},
    {"emoji": "👍", "delay": 5},
    {"emoji": "🔥", "delay": 9},
    {"emoji": "🥰", "delay": 9},
    {"emoji": "🎉", "delay": 11}
]

@app.route("/")
def home():
    return f"Smart Bot Farm Running. Loaded Bots: {len(BOT_TOKENS)}", 200

# Function na nagpapatakbo ng delay bago mag-react ang bot
def delayed_reaction(token, chat_id, message_id, emoji, delay_seconds):
    if delay_seconds > 0:
        time.sleep(delay_seconds)
        
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

        def create_webhook_handler(bot_token=token, bot_index=index):
            def handler():
                data = request.get_json(silent=True)
                if data and "channel_post" in data:
                    post = data["channel_post"]
                    chat_id = post["chat"]["id"]
                    message_id = post["message_id"]
                    
                    # Kukunin ang text ng post (gagawing lowercase para hindi seloso sa Capital Letters)
                    post_text = post.get("text", "").lower()

                    # Alamin kung anong emoji ang gagamitin para sa bot na ito
                    chosen_emoji = None
                    
                    # I-check kung may tumamang keyword sa loob ng text ng post
                    for keyword, emoji_list in KEYWORD_MAPPING.items():
                        if keyword in post_text:
                            # Pipiliin ang emoji na nakatoka sa index ng bot na ito
                            if bot_index < len(emoji_list):
                                chosen_emoji = emoji_list[bot_index]
                            break
                    
                    # Kung walang keyword na nahanap sa text, gamitin ang default kanina
                    if not chosen_emoji:
                        config = DEFAULT_CONFIGS[bot_index] if bot_index < len(DEFAULT_CONFIGS) else {"emoji": "❤️", "delay": 0}
                        chosen_emoji = config["emoji"]

                    # Kunin ang delay para sa bot na ito mula sa default settings
                    delay_config = DEFAULT_CONFIGS[bot_index] if bot_index < len(DEFAULT_CONFIGS) else {"emoji": "❤️", "delay": 0}
                    bot_delay = delay_config["delay"]

                    # Patakbuhin sa background gamit ang Threading
                    threading.Thread(
                        target=delayed_reaction,
                        args=(bot_token, chat_id, message_id, chosen_emoji, bot_delay)
                    ).start()

                return "ok", 200
            return handler

        app.add_url_rule(
            f"/{token}",
            endpoint=endpoint_name,
            view_func=create_webhook_handler(),
            methods=["POST"]
        )

setup_routes()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
