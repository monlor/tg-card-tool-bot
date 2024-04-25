import os
import requests
from dotenv import load_dotenv
import datetime
import re

from cache import Cache

load_dotenv()

MAIN_CURRENCY = os.getenv("MAIN_CURRENCY", "CNY")

EXCHANGERATE_API_KEY = os.getenv("EXCHANGERATE_API_KEY")

ECONOMIA_API = "https://economia.awesomeapi.com.br/json/daily/{}-{}/{}"

EXCHANGERATE_API = "https://v6.exchangerate-api.com/v6/{}/pair/{}/{}"

RATES_LIST = [
    { 'currency': 'USD', 'description': '🇺🇸 美元' }, 
    { 'currency': 'CNY', 'description': '🇨🇳 人民币' }, 
    { 'currency': 'GBP', 'description': '🇬🇧 英镑' }, 
    { 'currency': 'HKD', 'description': '🇭🇰 港币' }, 
    { 'currency': 'SGD', 'description': '🇸🇬 新元' }, 
    { 'currency': 'EUR', 'description': '🇪🇺 欧元' },
    { 'currency': 'CAD', 'description': '🇨🇦 加元' },
    { 'currency': 'JPY', 'description': '🇯🇵 日元' },
    { 'currency': 'PHP', 'description': '🇵🇭 比索' }, 
    { 'currency': 'MYR', 'description': '🇲🇾 令吉' }, 
    { 'currency': 'TRY', 'description': '🇹🇷 里拉' }, 
    { 'currency': 'NGN', 'description': '🇳🇬 奈拉' }, 
    { 'currency': 'ARS', 'description': '🇦🇷 比索' }
]

# 汇率缓存3小时
cache = Cache(default_expiration=86400)

def format_timestamp(t):
    dt = datetime.datetime.fromtimestamp(int(t))
    return dt.strftime('%Y-%m-%d')

def get_rates_from_economia(source, target):
    # jpy => usd 汇率错误
    if source in ['JPY']:
        return None
    data = []
    try:
        api_url = ECONOMIA_API.format(source, target, 1)
        response = requests.get(api_url)
        data = response.json()
    except requests.RequestException as e:
        print(f"请求错误: {e}")
        return None

    if not isinstance(data, list):
        return None

    return float(data[0]["bid"])

def get_rates_from_exchangerate(source, target):
    data = []
    try:
        api_url = EXCHANGERATE_API.format(EXCHANGERATE_API_KEY, source, target)
        response = requests.get(api_url)
        data = response.json()
    except requests.RequestException as e:
        print(f"请求错误: {e}")
        return None

    return float(data["conversion_rate"])

async def get_rates(source, target):

    # 取缓存
    rate = cache.get(f'{source}-{target}')

    if rate == None:

        rate = get_rates_from_economia(source, target)

        if (rate == None or rate == "") and EXCHANGERATE_API_KEY:
            rate = get_rates_from_exchangerate(source, target)
        
        # 设置缓存
        cache.set(f'{source}-{target}', rate)

    return rate

async def format_rate_response(source, target, amount, delay, rate):
    response = "💡 汇率换算\n"
    response += f"\n💹 汇率查询: 1 {source} = {rate} {target}\n"

    equiv_amount = amount * rate
    response += f"\n💰 货币换算: {amount} {source} = {equiv_amount:.2f} {target}\n"

    if delay != None:
        response += f"\n👋 将在{delay}秒后删除消息..."

    return response


async def format_rates_list(delay, main_currency):
    output = f"💡 汇率查询 1 {main_currency}\n\n"
    for c in RATES_LIST:
        if c['currency'] == main_currency:
            continue
        rate = await get_rates(main_currency, c['currency'])
        if rate != None:
            output += f"{c['description']}:  {rate}\n"

    if delay != None:
        output += f"\n👋 将在{delay}秒后删除消息..."

    return output


def find_rate_from_text(input_string):
    if input_string == None:
        return None, None
    pattern = r"(\d+)\s*([A-Za-z]{3})"
    match = re.search(pattern, input_string)

    if match:
        number = int(match.group(1))
        code = match.group(2)
        return number, code.upper()
    else:
        return None, None

async def rate_input_parse(input_text, quote):
    usage_text = 'Usage: /rate [货币，例如HKD] [金额]; /rate [来源货币] [目标货币] [来源金额]'
    command = input_text[0]
    source = None
    target = MAIN_CURRENCY
    amount = 0

    if command == '/ratec':
        target = 'CNY'
    elif command == '/rateu':
        target = 'USD'
    elif command == '/rateg':
        target = 'GBP'

    if len(input_text) == 3:
        if not re.match(r'^[A-Za-z]{3}$', input_text[1]) or not re.match(r'^\d+(\.\d+)?$', input_text[2]):
            return usage_text, source, target, amount
        source = input_text[1].upper()
        amount = float(input_text[2])
    elif len(input_text) == 4:
        if not re.match(r'^[A-Za-z]{3}$', input_text[1]) or not re.match(r'^[A-Za-z]{3}$', input_text[2]) or not re.match(r'^\d+(\.\d+)?$', input_text[3]):
            return usage_text, source, target, amount
        source = input_text[1].upper()
        target = input_text[2].upper()
        amount = float(input_text[3])
    elif len(input_text) == 2:
        if not re.match(r'^[A-Za-z]{3}$', input_text[1]):
            return usage_text, source, target, amount
        target = input_text[1].upper()
    elif len(input_text) == 1:
        if quote != None:
            # 如果引用文本中有金额和货币，则取引用文本的
            amount, source = find_rate_from_text(quote)
            if amount == None or source == None:
                return "😭 未识别到文本中的金额和货币信息！", source, target, amount
    else:
        return usage_text, source, target, amount

    return None, source, target, amount


# 汇率换算，存在key err,price,target_price,currency
async def do_exchange(items, currency):
    for item in items:
        if item['err'] != None:
            continue
        target_price = 0
        price = item['price']
        if price != None:
            if item['currency'] != currency:
                rate = await get_rates(item['currency'], currency)
                if rate != None:
                    target_price = price * rate
                else:
                    item['err'] = '汇率获取失败！'
            else:
                target_price = price
        else:
            item['err'] = '价格获取失败！'
        item['target_price'] = target_price

    return items