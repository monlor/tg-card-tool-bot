import os
from dotenv import load_dotenv
import aiogram
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
import asyncio

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
DELETE_DELAY = int(os.getenv("DELETE_DELAY", 60))

from rates import rate_input_parse, get_rates, format_rate_response, format_rates_list
from cardbin import cardbin_input_parse, get_bin, format_bin_response
from spotify import spotify_input_parse, format_spotify_prices
from netflix import netflix_input_parse, format_netflix_prices
from appstore import appstore_input_parse, format_appstore_prices

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

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
        print(f"Error deleting message: {e}")

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

@dp.message_handler(commands=['appstore', 'appstoreo'])
async def appstore_command(message: types.Message):
    input_text, quote = await parse_input(message)
    command = input_text[0]

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

    response = await format_appstore_prices(currency, country_code, app_name, app_id, delay, exchange)

    await processing_msg.edit_text(response)

    if delay is not None:
        asyncio.create_task(delete_message(processing_msg, delay))

if __name__ == '__main__':
    # executor.start_polling(dp, skip_updates=True)
    print('Bot started.')
    loop = asyncio.get_event_loop()
    loop.create_task(dp.start_polling())
    loop.run_forever()