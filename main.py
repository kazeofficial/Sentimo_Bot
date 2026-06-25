import asyncio
import random
import logging
import os
from threading import Thread
from flask import Flask
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

# ===== WEBKEEP ALIVE =====
app_web = Flask(__name__)
OWNER_ID = int(os.getenv("OWNER_ID", "0"))

@app_web.route("/")
def home():
    return "Bot is online!"

def keep_alive():
    port = int(os.environ.get("PORT", 10000))
    Thread(target=lambda: app_web.run(host="0.0.0.0", port=port)).start()
  
# I-setup ang logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

# Kukunin nito ang token mula sa Render Settings mamaya para tago at safe
BOT_TOKEN = os.getenv("BOT_TOKEN")

ALL_EMOJIS = ["👍", "🔥", "❤️", "🎉", "🤩", "🚀", "👏", "🙌", "🥰", "😎", "⚡", "💯"]

async def auto_react(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.channel_post:
        message_id = update.channel_post.message_id
        chat_id = update.channel_post.chat_id
        
        post_text = update.channel_post.text.lower() if update.channel_post.text else ""

        # Natural delay (2-4 seconds)
        delay = random.randint(2, 4)
        await asyncio.sleep(delay)

        chosen_reactions = []

        # Keyword matching
        if any(word in post_text for word in ["gcash", "pera", "kita", "sale", "promo", "discount"]):
            chosen_reactions = ["🤑", "💰", "🔥"]
        elif any(word in post_text for word in ["congrats", "salamat", "thank", "panalo", "lodi"]):
            chosen_reactions = ["🎉", "🙌", "👏", "❤️"]
        elif any(word in post_text for word in ["link", "website", "update", "bago", "news"]):
            chosen_reactions = ["🚀", "⚡", "🧐"]
        elif any(word in post_text for word in ["sad", "iyak", "sayang", "lugi", "bawi"]):
            chosen_reactions = ["😢", "💔", "🙏"]
        else:
            num_of_reactions = random.randint(3, 5)
            chosen_reactions = random.sample(ALL_EMOJIS, num_of_reactions)
        
        try:
            reaction_list = [{"type": "emoji", "emoji": emo} for emo in chosen_reactions]
            await context.bot.set_message_reaction(
                chat_id=chat_id,
                message_id=message_id,
                reaction=reaction_list
            )
            print(f"Sentimo_Bot reacted {chosen_reactions}")
        except Exception as e:
            print(f"Error: {e}")

def main():
    if not BOT_TOKEN:
        print("ERROR: Walang BOT_TOKEN na nahanap sa Environment Variables!")
        return

    # Gumawa ng malinis at isolated na asyncio event loop para sa Python 3.14+
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(MessageHandler(filters.UpdateType.CHANNEL_POSTS, auto_react))
    
    print("Sentimo_Bot is ONLINE via Render...")
    
    # Patakbuhin ang polling nang hindi sinasara nang biglaan ang loop
    application.run_polling(close_loop=False)

if __name__ == '__main__':
    keep_alive()  # Patakbuhin ang Flask web server mo sa background thread
    main()        # Patakbuhin ang Telegram Bot loop
