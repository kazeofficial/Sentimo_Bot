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
    return "Sentimo_Bot is online and running stable!"

def keep_alive():
    port = int(os.environ.get("PORT", 10000))
    Thread(target=lambda: app_web.run(host="0.0.0.0", port=port)).start()
  
# Logging Setup
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

BOT_TOKEN = os.getenv("BOT_TOKEN")
ALL_EMOJIS = ["👍", "🔥", "❤️", "🎉", "🤩", "🚀", "👏", "🙌", "🥰", "😎", "⚡", "💯"]

async def auto_react(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.channel_post:
        message_id = update.channel_post.message_id
        chat_id = update.channel_post.chat_id
        post_text = update.channel_post.text.lower() if update.channel_post.text else ""

        delay = random.randint(2, 4)
        await asyncio.sleep(delay)

        chosen_reactions = []
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
            print(f"Reaction Error: {e}")

def main():
    if not BOT_TOKEN:
        print("ERROR: Walang BOT_TOKEN sa Environment Variables!")
        return

    # 1. Patakbuhin ang Flask Keep-Alive Server
    keep_alive()

    # 2. Gamitin ang Builder pero i-off ang stop signals para iwas crash sa Python 3.14
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(MessageHandler(filters.UpdateType.CHANNEL_POSTS, auto_react))
    
    print("Sentimo_Bot is starting polling via Render Safe Mode...")
    
    # Ang stop_signals=None ang susi para hindi mag-crash ang loop sa background thread ng Render
    application.run_polling(stop_signals=None)

if __name__ == '__main__':
    main()
