import os
from dotenv import load_dotenv
from telegram import __version__ as TG_VER
import telegram.ext as tg
import re

from telegram import Update
from telegram.ext import Application, ApplicationBuilder, CommandHandler, ContextTypes

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
DELETE_DELAY = int(os.getenv("DELETE_DELAY", 60))
MAIN_CURRENCY = os.getenv("MAIN_CURRENCY", "CNY")

from rates import get_rates, format_rate_response
from cardbin import get_bin, format_bin_response

async def rate_command(update, context):
    input_text = update.message.text.split()
    usage_text = 'Usage: /rate [货币，例如HKD] [金额]; /rate [来源货币] [目标货币] [来源金额]'
    source = ""
    target = MAIN_CURRENCY
    amount = 0
    if len(input_text) == 3:
        if not re.match(r'^[A-Za-z]{3}$', input_text[1]) or not re.match(r'^\d+$', input_text[2]):
            await update.message.reply_text(usage_text)
            return
        source = input_text[1].upper()
        amount = float(input_text[2])
    elif len(input_text) == 4:
        if not re.match(r'^[A-Za-z]{3}$', input_text[1]) or not re.match(r'^[A-Za-z]{3}$', input_text[2]) or not re.match(r'^\d+$', input_text[3]):
            await update.message.reply_text(usage_text)
            return
        source = input_text[1].upper()
        target = input_text[2].upper()
        amount = float(input_text[3])
    else:
        await update.message.reply_text(usage_text)
        return
    
    rate = get_rates(source, target)
    response = ""
    if rate == None:
        response = "😭 查询失败，当前货币对可能不存在！"
    else:
        response = format_rate_response(source, target, amount, DELETE_DELAY, rate)
    
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
        ('rate', f'查询汇率'),
        ('bin', '查询银行卡BIN')
    ])

def main() -> None:
    """Start the bot."""
    application = Application.builder().token(TOKEN).post_init(post_init).build()
    print("Bot has been launched successfully!")
    application.run_polling()

if __name__ == '__main__':
    main()