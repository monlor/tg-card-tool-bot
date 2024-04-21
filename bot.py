import os
from dotenv import load_dotenv
from telegram import __version__ as TG_VER
import telegram.ext as tg
import re

from telegram import Update
from telegram.ext import Application, ApplicationBuilder, CommandHandler, ContextTypes

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
DELETE_DELAY = int(os.getenv("DELETE_DELAY", 30))
QUERY_DAYS = int(os.getenv("QUERY_DAYS", 5))
MAIN_CURRENCY = os.getenv("MAIN_CURRENCY", "USD")

from rates import get_rates, format_rate_response
from cardbin import get_bin, format_bin_response

async def rate_command(update, context):
    input_text = update.message.text.split()
    usage_text = 'Usage: /rate [目标货币，例如HKD] [金额]'
    if len(input_text) != 3:
        await update.message.reply_text(usage_text)
        return
    if not re.match(r'^[A-Za-z]{3}$', input_text[1]) or not re.match(r'^\d+$', input_text[2]):
        await update.message.reply_text(usage_text)
        return
    
    quote = input_text[1].upper()
    amount = float(input_text[2])
    
    rates = get_rates(quote)
    response = format_rate_response(quote, amount, rates)
    
    message = await update.message.reply_text(response)
    context.job_queue.run_once(delete_message, DELETE_DELAY, data=[message.chat_id, message.message_id, context.bot])

async def bin_command(update, context):
    input_text = update.message.text.split()
    usage_text = 'Usage: /bin [BIN号码6,8位]'
    if len(input_text) != 2:
        await update.message.reply_text(usage_text)
        return
    if len(input_text[1]) != 6 and len(input_text[1]) != 8:
        await update.message.reply_text(usage_text)
        return
    
    quote = input_text[1]
    
    bininfo = get_bin(quote)
    response = format_bin_response(quote, bininfo)
    
    message = await update.message.reply_text(response)
    context.job_queue.run_once(delete_message, DELETE_DELAY, data=[message.chat_id, message.message_id, context.bot])

async def delete_message(data):
    chat_id, message_id, bot = data.job.data
    await bot.delete_message(chat_id=chat_id, message_id=message_id)

async def post_init(application: Application) -> None:
    """Set up the bot commands and handlers."""
    application.add_handler(CommandHandler('rate', rate_command))
    application.add_handler(CommandHandler('bin', bin_command))

    await application.bot.set_my_commands([
        ('rate', f'查询最近{QUERY_DAYS}天兑换{MAIN_CURRENCY}的汇率'),
        ('bin', '查询银行卡BIN')
    ])

def main() -> None:
    """Start the bot."""
    application = Application.builder().token(TOKEN).post_init(post_init).build()
    print("Bot has been launched successfully!")
    application.run_polling()

if __name__ == '__main__':
    main()