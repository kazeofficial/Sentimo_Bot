import asyncio
import random
import logging
import os
from threading import Thread
from flask import Flask
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

# ===== WEBKEEP ALIVE (Para sa Render Web Service) =====
app_web = Flask(__name__)
OWNER_ID = int(os.getenv("OWNER_ID", "0"))

@app_web.route("/")
def home():
    return "Sentimo_Bot is online and active!"

def keep_alive():
    port = int(os.environ.get("PORT", 10000))
    Thread(target=lambda: app_web.run(host="0.0.0.0", port=port)).start()
  
# I-setup ang logging para sa Render Logs
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

# Kukunin ang token mula sa Render Environment Variables
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Listahan ng mga emojis para sa random reactions
ALL_EMOJIS = ["👍", "🔥", "❤️", "🎉", "🤩", "🚀", "👏", "🙌", "🥰", "😎", "⚡", "💯"]

async def auto_react(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.channel_post:
        message_id = update.channel_post.message_id
        chat_id = update.channel_post.chat_id
        
        post_text = update.channel_post.text.lower() if update.channel_post.text else ""

        # Natural delay (2-4 seconds) para magmukhang tao
        delay = random.randint(2, 4)
        await asyncio.sleep(delay)

        chosen_reactions = []

        # Keyword matching para sa matalinong reaksyon
        if any(word in post_text for word in ["gcash", "pera", "kita", "sale", "promo", "discount"]):
            chosen_reactions = ["🤑", "💰", "🔥"]
        elif any(word in post_text for word in ["congrats", "salamat", "thank", "panalo", "lodi"]):
            chosen_reactions = ["🎉", "🙌", "👏", "❤️"]
        elif any(word in post_text for word in ["link", "website", "update", "bago", "news"]):
            chosen_reactions = ["🚀", "⚡", "🧐"]
        elif any(word in post_text for word in ["sad", "iyak", "sayang", "lugi", "bawi"]):
            chosen_reactions = ["😢", "💔", "🙏"]
        else:
            # Random 3 hanggang 5 emojis kapag walang tumamang keyword
            num_of_reactions = random.randint(3, 5)
            chosen_reactions = random.sample(ALL_EMOJIS, num_of_reactions)
        
        try:
            reaction_list = [{"type": "emoji", "emoji": emo} for emo in chosen_reactions]
            await context.bot.set_message_reaction(
                chat_id=chat_id,
                message_id=message_id,
                reaction=reaction_list
            )
            print(f"Sentimo_Bot reacted {chosen_reactions} to message {message_id}")
        except Exception as e:
            print(f"Error handling reaction: {e}")

async def start_bot():
    """Dito manu-manong pinapatakbo ang bot para iwas-crash sa Python 3.14+"""
    if not BOT_TOKEN:
        print("ERROR: Walang BOT_TOKEN na nahanap sa Environment Variables!")
        return

    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(MessageHandler(filters.UpdateType.CHANNEL_POSTS, auto_react))
    
    # Init at start ng polling lifecycle nang hiwalay sa loop management ng library
    await application.initialize()
    await application.updater.start_polling()
    await application.start()
    
    print("Sentimo_Bot is ONLINE via Render (Async Safe Mode)...")
    
    # Panatilihing buhay ang task loop habang umaandar ang script
    while True:
        await asyncio.sleep(3600)

def main():
    # 1. Patakbuhin ang Flask web server sa hiwalay na thread
    keep_alive()
    
    # 2. Gumawa ng malinis na asyncio event loop at patakbuhin ang Telegram Bot doon
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(start_bot())

if __name__ == '__main__':
    main()
