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
from spotify import spotify_input_parse, format_spotify_prices
from netflix import netflix_input_parse, format_netflix_prices

def parse_input(update):
    input_text = update.message.text.split()
    replied_message = update.effective_message.reply_to_message
    quote = None

    if replied_message:
        quote = replied_message.text

    return input_text, quote

def get_delay(update):
    chat = update.effective_chat
    if chat.type == chat.PRIVATE:
        return None
    else:
        return DELETE_DELAY

async def rate_command(update, context):
    input_text, quote = parse_input(update)
    msg, source, target, amount = rate_input_parse(input_text, quote)
    if msg != None:
        await update.message.reply_text(msg)
        return
    delay = get_delay(update)

    # 先发送处理消息
    message = await update.message.reply_text("正在查询，请稍等...")

    response = ""
    if source == None:
        # 展示汇率列表
        response = format_rates_list(delay, target)
    else:
        # 计算来源汇率
        rate = get_rates(source, target)
        if rate == None:
            response = f"😭 查询失败，当前货币对 {source}:{target} 可能不存在！"
        else:
            response = format_rate_response(source, target, amount, delay, rate)
    
    await context.bot.edit_message_text(
        chat_id=update.effective_chat.id,
        message_id=message.message_id,
        text=response
    )

    if delay != None:
        context.job_queue.run_once(delete_message, delay, data=[message.chat_id, message.message_id, context.bot])

async def bin_command(update, context):

    input_text, quote = parse_input(update)

    msg, bin = cardbin_input_parse(input_text, quote)
    if msg != None:
        await update.message.reply_text(msg)
        return
    delay = get_delay(update)

    # 先发送处理消息
    message = await update.message.reply_text("正在查询，请稍等...")
        
    bininfo = get_bin(bin)
    response = format_bin_response(bin, bininfo, delay)
    
    await context.bot.edit_message_text(
        chat_id=update.effective_chat.id,
        message_id=message.message_id,
        text=response
    )
    if delay != None:
        context.job_queue.run_once(delete_message, delay, data=[message.chat_id, message.message_id, context.bot])

async def spotify_command(update, context):

    input_text, quote = parse_input(update)

    msg, currency = spotify_input_parse(input_text, quote)
    if msg != None:
        await update.message.reply_text(msg)
        return
    delay = get_delay(update)

    # 先发送处理消息
    message = await update.message.reply_text("正在查询，请稍等...")
        
    response = format_spotify_prices(currency, delay)
    
    await context.bot.edit_message_text(
        chat_id=update.effective_chat.id,
        message_id=message.message_id,
        text=response
    )
    if delay != None:
        context.job_queue.run_once(delete_message, delay, data=[message.chat_id, message.message_id, context.bot])

async def netflix_command(update, context):

    input_text, quote = parse_input(update)

    msg, currency = netflix_input_parse(input_text, quote)
    if msg != None:
        await update.message.reply_text(msg)
        return
    delay = get_delay(update)

    # 先发送处理消息
    message = await update.message.reply_text("正在查询，请稍等...")
        
    response = format_netflix_prices(currency, delay)
    
    await context.bot.edit_message_text(
        chat_id=update.effective_chat.id,
        message_id=message.message_id,
        text=response
    )
    if delay != None:
        context.job_queue.run_once(delete_message, delay, data=[message.chat_id, message.message_id, context.bot])

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
    application.add_handler(CommandHandler('spotify', spotify_command))
    application.add_handler(CommandHandler('netflix', netflix_command))

    await application.bot.set_my_commands([
        ('rate', '自定义汇率换算'),
        ('ratec', '汇率换算到CNY'),
        ('rateu', '汇率换算到USD'),
        ('rateg', '汇率换算到GBP'),
        ('bin', '查询银行卡BIN'),
        ('spotify', '查询各个地区Spotify的价格'),
        ('netflix', '查询各个地区Netflix的价格')
    ])

def main() -> None:
    """Start the bot."""
    application = Application.builder().token(TOKEN).post_init(post_init).build()
    print("Bot has been launched successfully!")
    application.run_polling()

if __name__ == '__main__':
    main()