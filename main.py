import os
import time
import random  # Para sa random delays
import threading
import requests
from flask import Flask, request

# Basahin ang magkakadugtong na tokens mula sa Render (comma-separated)
BOT_TOKENS_STR = os.getenv("BOT_TOKENS", "")
BOT_TOKENS = [token.strip() for token in BOT_TOKENS_STR.split(",") if token.strip()]

app = Flask(__name__)

# CONFIGURATION: Dito pumapasok ang mga matatalinong keywords mo.
# Tandaan: Mas mabuting maglagay ng variant tulad ng "paldoo" para masalo ang typos.
KEYWORD_MAPPING = {
    "sad": ["😢", "😭", "❤️", "😭", "😭"],       
    "solid": ["🎉", "❤️", "👏", "🔥", "❤️"],     
    "lol": ["😁", "❤️", "🙉", "😁", "👍"],      
    "paldo": ["😱", "🔥", "🔥", "🤩", "🎉"],
    "paldoo": ["😱", "🔥", "🔥", "🤩", "🎉"] # Para kahit may extra 'o', huli pa rin!
}

# DEFAULT CONFIGS: Gagamitin kung walang keyword sa post. 
# May min_delay at max_delay para maging random at natural ang pag-react ng mga bots.
DEFAULT_CONFIGS = [
    {"emoji": "❤️", "min_delay": 0, "max_delay": 2},   # Bot 1: Halos agad-agad (0-2s)
    {"emoji": "👍", "min_delay": 3, "max_delay": 6},   # Bot 2: Sa pagitan ng 3-6s
    {"emoji": "🔥", "min_delay": 7, "max_delay": 10},  # Bot 3: Sa pagitan ng 7-10s
    {"emoji": "🥰", "min_delay": 10, "max_delay": 14}, # Bot 4: Sa pagitan ng 10-14s
    {"emoji": "🎉", "min_delay": 14, "max_delay": 18}  # Bot 5: Sa pagitan ng 14-18s
]

@app.route("/")
def home():
    return f"Ultra Smart Bot Farm Running. Loaded Bots: {len(BOT_TOKENS)}", 200

# Function na nagpapatakbo ng delay bago mag-react ang bot gamit ang Telegram API
def delayed_reaction(token, chat_id, message_id, emoji, delay_seconds, is_big_effect):
    if delay_seconds > 0:
        time.sleep(delay_seconds) # Hihintay muna dito base sa nakuhang random seconds
        
    url = f"https://api.telegram.org/bot{token}/setMessageReaction"
    payload = {
        "chat_id": chat_id,
        "message_id": message_id,
        "reaction": [{"type": "emoji", "emoji": emoji}],
        "is_big": is_big_effect  # Malaking pagsabog/animation kapag True!
    }
    try:
        response = requests.post(url, json=payload, timeout=5)
        print(f"Bot {token[:10]}... reacted {emoji} (Delay: {delay_seconds:.2f}s, Big: {is_big_effect}) status: {response.status_code}")
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
                    
                    # FIX: Kukunin ang text kahit galing sa text post o sa media caption (Photo/Video)
                    post_text = post.get("text", "") or post.get("caption", "")
                    post_text = post_text.lower()

                    chosen_emoji = None
                    is_big_effect = False 

                    # MATALINONG PAG-CHECK NG KEYWORD:
                    for keyword, emoji_list in KEYWORD_MAPPING.items():
                        if keyword in post_text:
                            if bot_index < len(emoji_list):
                                chosen_emoji = emoji_list[bot_index]
                            
                            # FEATURE: Kung ang nahanap na keyword ay paldo o solid, may kasamang malaking animation!
                            if keyword in ["paldo", "paldoo", "solid"]:
                                is_big_effect = True
                            break # Hihinto na kapag nakahanap ng unang match
                    
                    # KUNG WALANG KEYWORD NA DETECTED, gagamit ng Default list mo
                    if not chosen_emoji:
                        config = DEFAULT_CONFIGS[bot_index] if bot_index < len(DEFAULT_CONFIGS) else {"emoji": "❤️"}
                        chosen_emoji = config.get("emoji", "❤️")

                    # FEATURE: Random delay calculation base sa min_delay at max_delay ng bot index
                    if bot_index < len(DEFAULT_CONFIGS):
                        cfg = DEFAULT_CONFIGS[bot_index]
                        bot_delay = random.uniform(cfg["min_delay"], cfg["max_delay"])
                    else:
                        bot_delay = random.uniform(0, 5)

                    # Patakbuhin sa background gamit ang Threading para hindi mag-timeout ang web request
                    threading.Thread(
                        target=delayed_reaction,
                        args=(bot_token, chat_id, message_id, chosen_emoji, bot_delay, is_big_effect)
                    ).start()

                return "ok", 200
            return handler

        # I-register ang ruta sa Flask app
        app.add_url_rule(
            f"/{token}",
            endpoint=endpoint_name,
            view_func=create_webhook_handler(),
            methods=["POST"]
        )

# Patakbuhin ang pag-setup ng mga ruta
setup_routes()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
