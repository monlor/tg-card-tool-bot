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

from rates import rate_input_parse, get_rates, format_rate_response, format_rates_list
from cardbin import cardbin_input_parse, get_bin, format_bin_response

def parse_input(update):
    input_text = update.message.text.split()
    replied_message = update.effective_message.reply_to_message
    quote = None
    if replied_message:
        quote = replied_message.text
    return input_text, quote

async def rate_command(update, context):
    input_text, quote = parse_input(update)
    msg, source, target, amount = rate_input_parse(input_text, quote)
    if msg != None:
        await update.message.reply_text(msg)
        return

    response = ""
    if source == None:
        # 展示汇率列表
        response = format_rates_list(DELETE_DELAY, target)
    else:
        # 计算来源汇率
        rate = get_rates(source, target)
        if rate == None:
            response = f"😭 查询失败，当前货币对 {source}:{target} 可能不存在！"
        else:
            response = format_rate_response(source, target, amount, DELETE_DELAY, rate)
    
    message = await update.message.reply_text(response)
    context.job_queue.run_once(delete_message, DELETE_DELAY, data=[message.chat_id, message.message_id, context.bot])

async def bin_command(update, context):

    input_text, quote = parse_input(update)

    msg, bin = cardbin_input_parse(input_text, quote)
    if msg != None:
        await update.message.reply_text(msg)
        return
        
    bininfo = get_bin(bin)
    response = format_bin_response(bin, bininfo)
    
    message = await update.message.reply_text(response)
    context.job_queue.run_once(delete_message, DELETE_DELAY, data=[message.chat_id, message.message_id, context.bot])

async def delete_message(data):
    chat_id, message_id, bot = data.job.data
    await bot.delete_message(chat_id=chat_id, message_id=message_id)

async def post_init(application: Application) -> None:
    """Set up the bot commands and handlers."""
    application.add_handler(CommandHandler('rate', rate_command))
    application.add_handler(CommandHandler('rateu', rate_command))
    application.add_handler(CommandHandler('ratec', rate_command))
    application.add_handler(CommandHandler('rateg', rate_command))
    application.add_handler(CommandHandler('bin', bin_command))

    await application.bot.set_my_commands([
        ('rate', '自定义汇率换算'),
        ('ratec', '汇率换算到CNY'),
        ('rateu', '汇率换算到USD'),
        ('rateg', '汇率换算到GBP'),
        ('bin', '查询银行卡BIN')
    ])

def main() -> None:
    """Start the bot."""
    application = Application.builder().token(TOKEN).post_init(post_init).build()
    print("Bot has been launched successfully!")
    application.run_polling()

if __name__ == '__main__':
    main()