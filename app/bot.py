import os
import logging
import dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

dotenv.load_dotenv()

# LOGGING (module-level is fine)
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is not set")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! How can I assist you my Master?")  # type: ignore

def run_bot() -> None:
    app = ApplicationBuilder().token(BOT_TOKEN).build() # type: ignore

    app.add_handler(CommandHandler("start", start))

    logger.info("Bot started")
    app.run_polling()