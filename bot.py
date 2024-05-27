import os
from dotenv import load_dotenv
import aiogram
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.types import BotCommand
import asyncio
import logging

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
DELETE_DELAY = int(os.getenv("DELETE_DELAY", 60))
REFRESH_CACHE = int(os.getenv("REFRESH_CACHE", 23))

from rates import rate_input_parse, get_rates, format_rate_response, format_rates_list
from cardbin import cardbin_input_parse, get_bin, format_bin_response
from spotify import spotify_input_parse, format_spotify_prices
from netflix import netflix_input_parse, format_netflix_prices
from appstore import appstore_input_parse, appstorea_input_parse, format_appstore_prices_one, format_appstore_prices_all

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# 配置日志记录器
logging.basicConfig(level=logging.INFO)

# 创建一个日志记录器
logger = logging.getLogger(__name__)

async def parse_input(message):
    input_text = message.text.split()
    quote = None

    if message.reply_to_message:
        quote = message.reply_to_message.text

    return input_text, quote

def get_delay(message):
    if message.chat.type == "private":
        return None
    else:
        return DELETE_DELAY

async def delete_message(message, delay):
    await asyncio.sleep(delay)
    try:
        await message.delete()
    except Exception as e:
        # Handle any exceptions that may occur during message deletion
        logger.info(f"Error deleting message: {e}")

@dp.message_handler(commands=['rate', 'rateu', 'ratec', 'rateg'])
async def rate_command(message: types.Message):
    input_text, quote = await parse_input(message)
    msg, source, target, amount = await rate_input_parse(input_text, quote)
    if msg is not None:
        await message.reply(msg)
        return
    delay = get_delay(message)

    # 先发送处理消息
    processing_msg = await message.reply("正在查询，请稍等...")

    response = ""
    if source is None:
        # 展示汇率列表
        response = await format_rates_list(delay, target)
    else:
        # 计算来源汇率
        rate = await get_rates(source, target)
        if rate is None:
            response = f"😭 查询失败，当前货币对 {source}:{target} 可能不存在！"
        else:
            response = await format_rate_response(source, target, amount, delay, rate)

    await processing_msg.edit_text(response)

    if delay is not None:
        asyncio.create_task(delete_message(processing_msg, delay))

@dp.message_handler(commands=['bin'])
async def bin_command(message: types.Message):
    input_text, quote = await parse_input(message)

    msg, bin = await cardbin_input_parse(input_text, quote)
    if msg is not None:
        await message.reply(msg)
        return
    delay = get_delay(message)

    # 先发送处理消息
    processing_msg = await message.reply("正在查询，请稍等...")

    response = await format_bin_response(bin, delay)

    await processing_msg.edit_text(response)

    if delay is not None:
        asyncio.create_task(delete_message(processing_msg, delay))

@dp.message_handler(commands=['spotify', 'spotifyo'])
async def spotify_command(message: types.Message):
    input_text, quote = await parse_input(message)
    command = input_text[0]

    msg, currency = await spotify_input_parse(input_text, quote)
    if msg is not None:
        await message.reply(msg)
        return
    delay = get_delay(message)

    exchange = True
    if command == '/spotifyo':
        exchange = False

    # 先发送处理消息
    processing_msg = await message.reply("正在查询，请稍等...")

    response = await format_spotify_prices(currency, delay, exchange)

    await processing_msg.edit_text(response)

    if delay is not None:
        asyncio.create_task(delete_message(processing_msg, delay))

@dp.message_handler(commands=['netflix', 'netflixo'])
async def netflix_command(message: types.Message):
    input_text, quote = await parse_input(message)
    command = input_text[0]

    msg, currency = await netflix_input_parse(input_text, quote)
    if msg is not None:
        await message.reply(msg)
        return
    delay = get_delay(message)

    exchange = True
    if command == '/netflixo':
        exchange = False

    # 先发送处理消息
    processing_msg = await message.reply("正在查询，请稍等...")

    response = await format_netflix_prices(currency, delay, exchange)

    await processing_msg.edit_text(response)

    if delay is not None:
        asyncio.create_task(delete_message(processing_msg, delay))

@dp.message_handler(commands=['appstore', 'appstoreo', 'appstorea'])
async def appstore_command(message: types.Message):
    input_text, quote = await parse_input(message)
    command = input_text[0]

    if command == '/appstorea':
        msg, currency, country_code, app_name, app_id = await appstorea_input_parse(input_text, quote)
    else:
        msg, currency, country_code, app_name, app_id = await appstore_input_parse(input_text, quote)

    if msg is not None:
        await message.reply(msg)
        return
    delay = get_delay(message)

    exchange = True
    if command == '/appstoreo':
        exchange = False

    # 先发送处理消息
    processing_msg = await message.reply("正在查询，请稍等...")

    if command == '/appstorea':
        response = await format_appstore_prices_all(currency, app_name, app_id, delay, exchange)
    else:
        response = await format_appstore_prices_one(currency, country_code, app_name, app_id, delay, exchange)

    await processing_msg.edit_text(response)

    if delay is not None:
        asyncio.create_task(delete_message(processing_msg, delay))

# 处理未知命令
@dp.message_handler(commands=[])
async def unknown_command(message: types.Message):
    await message.reply('抱歉,我不认识这个命令。请输入 / 查看可用命令。')

async def refresh_cache():
    while True:
        logger.info("Refresh cache for Netflix ...")
        await format_netflix_prices('CNY', None, True)

        logger.info("Refresh cache for Spotify ...")
        await format_spotify_prices('CNY', None, True)

        logger.info("Refresh cache for ratec ...")
        await format_rates_list(None, 'CNY')

        logger.info("Refresh cache for rateu ...")
        await format_rates_list(None, 'USD')

        logger.info("Refresh cache for rateg ...")
        await format_rates_list(None, 'GBP')

        wait_time = 60 * 60 * REFRESH_CACHE

        logger.info(f'Wait {REFRESH_CACHE} hours ...')

        await asyncio.sleep(wait_time)

async def set_bot_commands(dp: Dispatcher):
    bot_commands = [
        BotCommand(command='/rate', description='自定义汇率换算'),
        BotCommand(command='/ratec', description='汇率换算到 CNY'),
        BotCommand(command='/rateu', description='汇率换算到 USD'),
        BotCommand(command='/rateg', description='汇率换算到 GBP'),
        BotCommand(command='/bin', description='查询银行卡 BIN'),
        BotCommand(command='/spotify', description='查询 Spotify 汇率换算价格'),
        BotCommand(command='/spotifyo', description='查询 Spotify 当地货币价格'),
        BotCommand(command='/netflix', description='查询 NetFlix 汇率换算价格'),
        BotCommand(command='/netflixo', description='查询 NetFlix 当地货币价格'),
        BotCommand(command='/appstore', description='查询 AppStore 汇率换算价格'),
        BotCommand(command='/appstoreo', description='查询 AppStore 当地货币价格'),
        BotCommand(command='/appstorea', description='查询 AppStore 多个常见地区的价格进行对比'),
    ]
    await bot.set_my_commands(bot_commands)

if __name__ == '__main__':
    # executor.start_polling(dp, skip_updates=True)
    logger.info('Bot started.')
    loop = asyncio.get_event_loop()
    loop.create_task(executor.start_polling(dp, skip_updates=True, on_startup=set_bot_commands))
    if REFRESH_CACHE != 0:
        loop.create_task(refresh_cache())
    loop.run_forever()