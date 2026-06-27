import os
import time
import random  # Para sa random delays, shuffling, at choice
import threading
import requests
from flask import Flask, request

BOT_TOKENS_STR = os.getenv("BOT_TOKENS", "")
BOT_TOKENS = [token.strip() for token in BOT_TOKENS_STR.split(",") if token.strip()]

app = Flask(__name__)

# 📌 KEYWORD MAPPING: Binago at nilagyan ng DUPLICATES gamit lang ang 9 na saktong emojis mo!
KEYWORD_MAPPING = {
    "sad": ["❤️", "❤️", "❤️", "👍", "👍", "😢", "👏", "😢", "😥", "🙈", "🙈", "❤️", "😢", "👏", "🥰"],       
    "solid": ["🔥", "🔥", "🔥", "👍", "👍", "👏", "👏", "🤩", "🤩", "😍", "😍", "❤️", "🔥", "👍", "🤩"],     
    "lol": ["😁", "😁", "😁", "🙈", "🙈", "👍", "👍", "❤️", "❤️", "🤩", "🤩", "😍", "😁", "🙈", "👍"],      
    "paldo": ["🔥", "🔥", "🔥", "🤩", "🤩", "😍", "😍", "❤️", "❤️", "👍", "👍", "🥰", "🔥", "🤩", "😍"],
    "paldoo": ["🔥", "🔥", "🔥", "🤩", "🤩", "🔥", "❤️", "❤️", "🙈", "👍", "👍", "🥰", "🔥", "😁", "😍"]
}

# 🎲 BASE REACTIONS: Mula sa Screenshot_20260627-115647.jpg (Walang sad emoji)
SAFE_EMOJIS = ["❤️", "👍", "🔥", "🥰", "👏", "😁", "🙈", "😍", "🤩"]

# DEFAULT CONFIGS: Ang tamang gap para sa 15 bots mo
DEFAULT_CONFIGS = [
    {"min_delay": 0, "max_delay": 2},     # Bot 1
    {"min_delay": 2, "max_delay": 5},     # Bot 2
    {"min_delay": 5, "max_delay": 8},     # Bot 3
    {"min_delay": 8, "max_delay": 11},    # Bot 4
    {"min_delay": 11, "max_delay": 14},   # Bot 5
    {"min_delay": 14, "max_delay": 17},   # Bot 6
    {"min_delay": 17, "max_delay": 20},   # Bot 7
    {"min_delay": 20, "max_delay": 23},   # Bot 8
    {"min_delay": 23, "max_delay": 26},   # Bot 9
    {"min_delay": 26, "max_delay": 29},   # Bot 10
    {"min_delay": 29, "max_delay": 32},   # Bot 11
    {"min_delay": 32, "max_delay": 35},   # Bot 12
    {"min_delay": 35, "max_delay": 38},   # Bot 13
    {"min_delay": 38, "max_delay": 40},   # Bot 14
    {"min_delay": 40, "max_delay": 42}    # Bot 15
]

@app.route("/")
def home():
    return f"Ultra Random Bot Farm Running. Loaded Bots: {len(BOT_TOKENS)}", 200

def delayed_reaction(token, chat_id, message_id, emoji, delay_seconds, is_big_effect):
    if delay_seconds > 0:
        time.sleep(delay_seconds)
        
    url = f"https://api.telegram.org/bot{token}/setMessageReaction"
    payload = {
        "chat_id": chat_id,
        "message_id": message_id,
        "reaction": [{"type": "emoji", "emoji": emoji}],
        "is_big": is_big_effect  
    }
    try:
        requests.post(url, json=payload, timeout=5)
    except Exception as e:
        print(f"Error sa reaction: {e}")

@app.route("/webhook", methods=["POST"])
def unified_webhook():
    data = request.get_json(silent=True)
    if data and "channel_post" in data:
        post = data["channel_post"]
        chat_id = post["chat"]["id"]
        message_id = post["message_id"]
        
        post_text = post.get("text", "") or post.get("caption", "")
        post_text = post_text.lower()

        bot_tasks = []

        for bot_index, token in enumerate(BOT_TOKENS):
            chosen_emoji = None
            is_big_effect = False 

            # Check keyword match
            for keyword, emoji_list in KEYWORD_MAPPING.items():
                if keyword in post_text:
                    if bot_index < len(emoji_list):
                        chosen_emoji = emoji_list[bot_index]
                    if keyword in ["paldo", "paldoo", "solid"]:
                        is_big_effect = True
                    break 
            
            # KUNG WALANG KEYWORD: Random choice pa rin mula sa 9 safe emojis (May duplicates)
            if not chosen_emoji:
                chosen_emoji = random.choice(SAFE_EMOJIS)
                is_big_effect = True 

            # Kumuha ng delay base sa pinalawak nating config list
            if bot_index < len(DEFAULT_CONFIGS):
                cfg = DEFAULT_CONFIGS[bot_index]
                bot_delay = random.uniform(cfg["min_delay"], cfg["max_delay"])
            else:
                bot_delay = random.uniform(40, 50)

            bot_tasks.append((token, chat_id, message_id, chosen_emoji, bot_delay, is_big_effect))

        # 🎲 I-shuffle ang pagkakasunod-sunod para mas sabog ang pasok!
        random.shuffle(bot_tasks)

        # Patakbuhin silang lahat sa background
        for task in bot_tasks:
            threading.Thread(target=delayed_reaction, args=task).start()

    return "ok", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
