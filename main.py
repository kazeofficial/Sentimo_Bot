import os
import time
import random
import threading
import requests
from flask import Flask, request

# TOKENS CONFIG
BOT_TOKENS_STR = os.getenv("BOT_TOKENS", "")
BOT_TOKENS = list(dict.fromkeys([token.strip() for token in BOT_TOKENS_STR.split(",") if token.strip()]))

# MASTER CONTROL BOT CONFIG
MASTER_TOKEN = "8767828114:AAG_c4L2YTq5sOighTwuLcSMxv3w0UDjgXM"
ADMIN_ID = 7201369115  # 🎯 Saktong Admin ID mo

# PRIVATE CHANNELS WHITELIST
ALLOWED_CHANNELS = [-1004483652219, -1002980077999]  # 🎯 Saktong Channels mo

app = Flask(__name__)

# GLOBAL STATES
FARM_ACTIVE = True
SPREAD_TIME_MINUTES = 0  

KEYWORD_MAPPING = {
    "sad": ["❤️", "❤️", "❤️", "👍", "👍", "👏", "👏", "🥰", "🥰", "🙈", "🙈", "❤️", "👍", "👏", "🥰"],       
    "solid": ["🔥", "🔥", "🔥", "👍", "👍", "👏", "👏", "🤩", "🤩", "😍", "😍", "❤️", "🔥", "👍", "🤩"],     
    "lol": ["😁", "😁", "😁", "🙈", "🙈", "👍", "👍", "❤️", "❤️", "🤩", "🤩", "😍", "😁", "🙈", "👍"],      
    "paldo": ["🔥", "🔥", "🔥", "🤩", "🤩", "😍", "😍", "❤️", "❤️", "👍", "👍", "🥰", "🔥", "🤩", "😍"],
    "paldoo": ["🔥", "🔥", "🔥", "🤩", "🤩", "😍", "😍", "❤️", "❤️", "👍", "👍", "🥰", "🔥", "🤩", "😍"]
}

SAFE_EMOJIS = ["❤️", "👍", "🔥", "🥰", "👏", "😁", "🙈", "😍", "🤩"]

DEFAULT_CONFIGS = [
    {"min_delay": 0, "max_delay": 2}, {"min_delay": 2, "max_delay": 5},
    {"min_delay": 5, "max_delay": 8}, {"min_delay": 8, "max_delay": 11},
    {"min_delay": 11, "max_delay": 14}, {"min_delay": 14, "max_delay": 17},
    {"min_delay": 17, "max_delay": 20}, {"min_delay": 20, "max_delay": 23},
    {"min_delay": 23, "max_delay": 26}, {"min_delay": 26, "max_delay": 29},
    {"min_delay": 29, "max_delay": 32}, {"min_delay": 32, "max_delay": 35},
    {"min_delay": 35, "max_delay": 38}, {"min_delay": 38, "max_delay": 40},
    {"min_delay": 40, "max_delay": 42}
]

@app.route("/")
def home():
    return f"FARM: {'ACTIVE' if FARM_ACTIVE else 'OFF'} | Spread: {SPREAD_TIME_MINUTES}m | Bots: {len(BOT_TOKENS)}", 200

def send_master_message(chat_id, text, reply_markup=None):
    url = f"https://api.telegram.org/bot{MASTER_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
    if reply_markup:
        payload["reply_markup"] = reply_markup
    requests.post(url, json=payload, timeout=5)

def get_control_panel_keyboard():
    status_text = "🟢 FARM ONLINE" if FARM_ACTIVE else "🔴 FARM OFFLINE"
    d0 = "🔘 No Delay" if SPREAD_TIME_MINUTES == 0 else "⏱️ No Delay"
    d5 = "🔘 5 Mins Spread" if SPREAD_TIME_MINUTES == 5 else "⏱️ 5 Mins Spread"
    d10 = "🔘 10 Mins Spread" if SPREAD_TIME_MINUTES == 10 else "⏱️ 10 Mins Spread"
    
    return {
        "inline_keyboard": [
            [{"text": status_text, "callback_data": "toggle_status"}],
            [
                {"text": d0, "callback_data": "set_spread_0"},
                {"text": d5, "callback_data": "set_spread_5"},
                {"text": d10, "callback_data": "set_spread_10"}
            ],
            [{"text": "🔄 Refresh Status", "callback_data": "refresh"}]
        ]
    }

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
    except Exception:
        pass

@app.route("/webhook", methods=["POST"])
def unified_webhook():
    global FARM_ACTIVE, SPREAD_TIME_MINUTES
    data = request.get_json(silent=True)
    if not data:
        return "ok", 200

    # 1. CONTROL PANEL
    if "message" in data:
        msg = data["message"]
        chat_id = msg["chat"]["id"]
        user_id = msg["from"]["id"]
        text = msg.get("text", "")

        if user_id != ADMIN_ID:
            return "ok", 200

        if text == "/start":
            panel_text = (
                "🤖 *KAZEHAYAMODZ BOT REACTION CONTROL PANEL*\n"
                "--------------------------------------------\n"
                f"Status: `{'ACTIVE' if FARM_ACTIVE else 'OFF'}`\n"
                f"Mode: `Random Spread`\n"
                f"Max Windows Time: `{SPREAD_TIME_MINUTES} minutes`"
            )
            send_master_message(chat_id, panel_text, get_control_panel_keyboard())

    # 2. INLINE BUTTONS
    elif "callback_query" in data:
        query = data["callback_query"]
        user_id = query["from"]["id"]
        chat_id = query["message"]["chat"]["id"]
        query_id = query["id"]
        callback_data = query["data"]

        if user_id != ADMIN_ID:
            requests.post(f"https://api.telegram.org/bot{MASTER_TOKEN}/answerCallbackQuery", json={"callback_query_id": query_id, "text": "Bawal ka rito!", "show_alert": True})
            return "ok", 200

        if callback_data == "toggle_status":
            FARM_ACTIVE = not FARM_ACTIVE
        elif callback_data == "set_spread_0":
            SPREAD_TIME_MINUTES = 0
        elif callback_data == "set_spread_5":
            SPREAD_TIME_MINUTES = 5
        elif callback_data == "set_spread_10":
            SPREAD_TIME_MINUTES = 10

        updated_text = (
            "🤖 *KAZEHAYAMODZ BOT REACTION CONTROL PANEL*\n"
            "--------------------------------------------\n"
            f"Status: `{'ACTIVE' if FARM_ACTIVE else 'OFF'}`\n"
            f"Mode: `Random Spread`\n"
            f"Max Windows Time: `{SPREAD_TIME_MINUTES} minutes`"
        )
        
        url = f"https://api.telegram.org/bot{MASTER_TOKEN}/editMessageText"
        payload = {
            "chat_id": chat_id,
            "message_id": query["message"]["message_id"],
            "text": updated_text,
            "parse_mode": "Markdown",
            "reply_markup": get_control_panel_keyboard()
        }
        requests.post(url, json=payload, timeout=5)
        requests.post(f"https://api.telegram.org/bot{MASTER_TOKEN}/answerCallbackQuery", json={"callback_query_id": query_id, "text": "Spread setting updated!"})

    # 3. REACTION FARM
    elif "channel_post" in data:
        if not FARM_ACTIVE:
            return "ok", 200

        post = data["channel_post"]
        chat_id = post["chat"]["id"]
        message_id = post["message_id"]

        if chat_id not in ALLOWED_CHANNELS:
            return "ok", 200
        
        post_text = post.get("text", "") or post.get("caption", "")
        post_text = post_text.lower()

        bot_tasks = []
        total_seconds = SPREAD_TIME_MINUTES * 60

        shuffled_tokens = list(BOT_TOKENS)
        random.shuffle(shuffled_tokens)

        for bot_index, token in enumerate(shuffled_tokens):
            chosen_emoji = None
            is_big_effect = False 

            for keyword, emoji_list in KEYWORD_MAPPING.items():
                if keyword in post_text:
                    if bot_index < len(emoji_list):
                        chosen_emoji = emoji_list[bot_index]
                    if keyword in ["paldo", "paldoo", "solid"]:
                        is_big_effect = True
                    break 
            
            if not chosen_emoji:
                chosen_emoji = random.choice(SAFE_EMOJIS)
                is_big_effect = True 

            # RANDOM SPREAD MODE
            if SPREAD_TIME_MINUTES > 0:
                bot_delay = random.uniform(0, total_seconds)
            else:
                if bot_index < len(DEFAULT_CONFIGS):
                    cfg = DEFAULT_CONFIGS[bot_index]
                    bot_delay = random.uniform(cfg["min_delay"], cfg["max_delay"])
                else:
                    bot_delay = random.uniform(40, 50)

            bot_tasks.append((token, chat_id, message_id, chosen_emoji, bot_delay, is_big_effect))

        for task in bot_tasks:
            threading.Thread(target=delayed_reaction, args=task).start()

    return "ok", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
