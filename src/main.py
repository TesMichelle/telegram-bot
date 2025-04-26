import asyncio
import time

import logging
import telegram
from telegram import Update
from telegram.ext import Application, ContextTypes, CommandHandler

import os
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

from getPrice import get_price_bybit as get_price

TOKEN = os.environ['BOTTOKEN']

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends explanation on how to use the bot."""
    await update.message.reply_text("Hi! Use /set <price_low> <price_high> to set a price notification")

async def check_price(context: ContextTypes.DEFAULT_TYPE) -> None:
    """get and check the price"""
    price = get_price()
    job = context.job
    if (price < job.data[0]) or (price > job.data[1]) :
        await context.bot.send_message(job.chat_id, text=f"Price: {price}$! {job.data[0]}$-{job.data[1]}$ is left.")
        remove_job_if_exists(str(job.chat_id), context)

def remove_job_if_exists(name: str, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Remove job with given name. Returns whether job was removed."""
    current_jobs = context.job_queue.get_jobs_by_name(name)
    if not current_jobs:
        return False
    for job in current_jobs:
        job.schedule_removal()
    return True

async def set_notification(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Add a job to the queue."""
    chat_id = update.effective_message.chat_id
    try:
        # args[0] should contain the time for the timer in seconds
        price_low = float(context.args[0])
        price_high = 999999
        if len(context.args) == 2:
            price_high = float(context.args[1])
        if (price_low < 0) or (price_low > price_high) or (price_high < 0):
            await update.effective_message.reply_text("Sorry we can not set such window!")
            return

        job_removed = remove_job_if_exists(str(chat_id), context)
        context.job_queue.run_repeating(check_price, interval=60, first=5,
            chat_id=chat_id, name=str(chat_id), data=[price_low, price_high])

        text = "Notification successfully set!"
        if job_removed:
            text += " Old one was removed."
        await update.effective_message.reply_text(text)

    except (IndexError, ValueError):
        await update.effective_message.reply_text("Usage: /set <price_low> <price_high>")

async def unset(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Remove the job if the user changed their mind."""
    chat_id = update.message.chat_id
    job_removed = remove_job_if_exists(str(chat_id), context)
    text = "Norification successfully cancelled!" if job_removed else "You have no active notifications!."
    await update.message.reply_text(text)

def main() -> None:
    """Run bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(TOKEN).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler(["start", "help"], start))
    application.add_handler(CommandHandler("set", set_notification))
    application.add_handler(CommandHandler("unset", unset))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
