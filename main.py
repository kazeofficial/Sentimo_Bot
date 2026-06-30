import os
import time
import random
import threading
import requests
from flask import Flask, request

# TOKENS CONFIG
BOT_TOKENS_STR = os.getenv("BOT_TOKENS", "")
BOT_TOKENS = [token.strip() for token in BOT_TOKENS_STR.split(",") if token.strip()]

# MASTER CONTROL BOT CONFIG
MASTER_TOKEN = "8767828114:AAG_c4L2YTq5sOighTwuLcSMxv3w0UDjgXM"
ADMIN_ID = 7201369115  # ⚠️ PALITAN MO ITO NG IYONG HALONG TELEGRAM USER ID!

# PRIVATE CHANNELS WHITELIST
# ⚠️ Ilagay mo rito ang mga ID ng channels mo kung saan LANG pwedeng gumana ang bots.
# Tandaan: Ang channel ID sa Telegram ay laging nagsisimula sa -100 (Halimbawa: -100223456789)
ALLOWED_CHANNELS = [-1002980077999, -1004483652219] 

app = Flask(__name__)

# GLOBAL STATES (Mga pwedeng baguhin sa Control Panel)
FARM_ACTIVE = True
EXTRA_DELAY_MINUTES = 0  # Dagdag na hihintayin bago magsimula ang farm

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
    return f"FARM: {'ACTIVE' if FARM_ACTIVE else 'OFF'} | Extra Delay: {EXTRA_DELAY_MINUTES}m | Bots: {len(BOT_TOKENS)}", 200

def send_master_message(chat_id, text, reply_markup=None):
    url = f"https://api.telegram.org/bot{MASTER_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
    if reply_markup:
        payload["reply_markup"] = reply_markup
    requests.post(url, json=payload, timeout=5)

def get_control_panel_keyboard():
    status_text = "🟢 FARM ONLINE" if FARM_ACTIVE else "🔴 FARM OFFLINE"
    delay_text = f"⏳ Extra Delay: {EXTRA_DELAY_MINUTES} mins"
    
    return {
        "inline_keyboard": [
            [{"text": status_text, "callback_data": "toggle_status"}],
            [
                {"text": "⏱️ No Delay", "callback_data": "delay_0"},
                {"text": "⏱️ 5 Mins", "callback_data": "delay_5"},
                {"text": "⏱️ 10 Mins", "callback_data": "delay_10"}
            ],
            [{"text": "🔄 Refresh Status", "callback_data": "refresh"}]
        ]
    }

def delayed_reaction(token, chat_id, message_id, emoji, delay_seconds, is_big_effect):
    # Idagdag ang Extra Delay mula sa Control Panel (Minutes to Seconds)
    total_delay = delay_seconds + (EXTRA_DELAY_MINUTES * 60)
    if total_delay > 0:
        time.sleep(total_delay)
        
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
    global FARM_ACTIVE, EXTRA_DELAY_MINUTES
    data = request.get_json(silent=True)
    if not data:
        return "ok", 200

    # 1. KONTROL PARA SA PRIVATE MASTER CONTROL PANEL (Direct Message sa Master Bot)
    if "message" in data:
        msg = data["message"]
        chat_id = msg["chat"]["id"]
        user_id = msg["from"]["id"]
        text = msg.get("text", "")

        # SECURITY CHECK: Kung hindi ikaw ang nag-chat, iblock ang bot.
        if user_id != ADMIN_ID:
            return "ok", 200

        if text == "/start":
            panel_text = (
                "🤖 *KAZEHAYAMODZ BOT REACTION CONTROL PANEL*\n"
                "--------------------------------------------\n"
                f"Status: `{'ACTIVE' if FARM_ACTIVE else 'OFF'}`\n"
                f"Extra Wait Time: `{EXTRA_DELAY_MINUTES} minutes`"
            )
            send_master_message(chat_id, panel_text, get_control_panel_keyboard())

    # 2. HANDLING NG INLINE BUTTON CLICKS
    elif "callback_query" in data:
        query = data["callback_query"]
        user_id = query["from"]["id"]
        chat_id = query["message"]["chat"]["id"]
        query_id = query["id"]
        callback_data = query["data"]

        # SECURITY CHECK: Ikaw lang ang pwedeng pumindot ng buttons
        if user_id != ADMIN_ID:
            requests.post(f"https://api.telegram.org/bot{MASTER_TOKEN}/answerCallbackQuery", json={"callback_query_id": query_id, "text": "Bawal ka rito!", "show_alert": True})
            return "ok", 200

        # Actions base sa pinindot mo
        if callback_data == "toggle_status":
            FARM_ACTIVE = not FARM_ACTIVE
        elif callback_data == "delay_0":
            EXTRA_DELAY_MINUTES = 0
        elif callback_data == "delay_5":
            EXTRA_DELAY_MINUTES = 5
        elif callback_data == "delay_10":
            EXTRA_DELAY_MINUTES = 10

        # I-update ang panel matapos pindutin
        updated_text = (
            "🤖 *KAZEHAYAMODZ BOT REACTION CONTROL PANEL*\n"
            "--------------------------------------------\n"
            f"Status: `{'ACTIVE' if FARM_ACTIVE else 'OFF'}`\n"
            f"Extra Wait Time: `{EXTRA_DELAY_MINUTES} minutes`"
        )
        
        # Edit current message
        url = f"https://api.telegram.org/bot{MASTER_TOKEN}/editMessageText"
        payload = {
            "chat_id": chat_id,
            "message_id": query["message"]["message_id"],
            "text": updated_text,
            "parse_mode": "Markdown",
            "reply_markup": get_control_panel_keyboard()
        }
        requests.post(url, json=payload, timeout=5)
        
        # Acknowledge the click
        requests.post(f"https://api.telegram.org/bot{MASTER_TOKEN}/answerCallbackQuery", json={"callback_query_id": query_id, "text": "Settings updated!"})

    # 3. KONTROL PARA SA MGA CHANNELS (REACTION FARM)
    elif "channel_post" in data:
        # SECURITY CHECK: Kung NAKA-OFF ang farm sa panel, huwag mag-react.
        if not FARM_ACTIVE:
            return "ok", 200

        post = data["channel_post"]
        chat_id = post["chat"]["id"]
        message_id = post["message_id"]

        # SECURITY CHECK: PRIVATE BOT PROTECTION
        # Kung ang nag-post na channel ay HINDI kasama sa whitelisted channels mo, automatic BLOCK!
        if chat_id not in ALLOWED_CHANNELS:
            print(f"Blocked un-authorized channel reaction request from: {chat_id}")
            return "ok", 200
        
        post_text = post.get("text", "") or post.get("caption", "")
        post_text = post_text.lower()

        bot_tasks = []

        for bot_index, token in enumerate(BOT_TOKENS):
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

            if bot_index < len(DEFAULT_CONFIGS):
                cfg = DEFAULT_CONFIGS[bot_index]
                bot_delay = random.uniform(cfg["min_delay"], cfg["max_delay"])
            else:
                bot_delay = random.uniform(40, 50)

            bot_tasks.append((token, chat_id, message_id, chosen_emoji, bot_delay, is_big_effect))

        random.shuffle(bot_tasks)

        for task in bot_tasks:
            threading.Thread(target=delayed_reaction, args=task).start()

    return "ok", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
