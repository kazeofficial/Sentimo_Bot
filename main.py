import os
import time
import random  # Para sa random delays at shuffling
import threading
import requests
from flask import Flask, request

BOT_TOKENS_STR = os.getenv("BOT_TOKENS", "")
BOT_TOKENS = [token.strip() for token in BOT_TOKENS_STR.split(",") if token.strip()]

app = Flask(__name__)

# KEYWORD MAPPING: Narito pa rin ang custom keyword shortcuts mo
KEYWORD_MAPPING = {
    "sad": ["😢", "😭", "❤️", "😭", "😭"],       
    "solid": ["🎉", "❤️", "👏", "🔥", "❤️"],     
    "lol": ["😁", "❤️", "🙈", "😁", "👍"],      
    "paldo": ["😱", "🔥", "🔥", "🤩", "🎉"],
    "paldoo": ["😱", "🔥", "🔥", "🤩", "🎉"]
}

# 🎲 BASE REACTIONS: Kinuha mismo sa channel settings mo (Tinanggal ang 😭 at 🥲)
SAFE_EMOJIS = ["❤️", "🔥", "🥰", "👏", "😁", "🎉", "⚡", "🤩", "😍", "🫡", "👌", "😱", "🙈"]

# DEFAULT CONFIGS: Random delays kada bot para natural tingnan ang pag-react
DEFAULT_CONFIGS = [
    {"min_delay": 0, "max_delay": 2},   
    {"min_delay": 3, "max_delay": 6},   
    {"min_delay": 7, "max_delay": 10},  
    {"min_delay": 10, "max_delay": 14}, 
    {"min_delay": 14, "max_delay": 18}  
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

        # Pipili ng magkakaibang random emojis para sa bawat bot galing sa base list ng channel mo
        random_default_emojis = random.sample(SAFE_EMOJIS, min(len(BOT_TOKENS), len(SAFE_EMOJIS)))

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
            
            # KUNG WALANG KEYWORD: Random na mula sa safe list ng channel mo ang kukunin
            if not chosen_emoji:
                if bot_index < len(random_default_emojis):
                    chosen_emoji = random_default_emojis[bot_index]
                else:
                    chosen_emoji = random.choice(SAFE_EMOJIS)
                
                is_big_effect = True # Naka-pasabog effect na rin para buhay!

            if bot_index < len(DEFAULT_CONFIGS):
                cfg = DEFAULT_CONFIGS[bot_index]
                bot_delay = random.uniform(cfg["min_delay"], cfg["max_delay"])
            else:
                bot_delay = random.uniform(0, 5)

            bot_tasks.append((token, chat_id, message_id, chosen_emoji, bot_delay, is_big_effect))

        # 🎲 I-shuffle para paiba-iba ang unahan
        random.shuffle(bot_tasks)

        # Patakbuhin silang lahat sa background
        for task in bot_tasks:
            threading.Thread(target=delayed_reaction, args=task).start()

    return "ok", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
