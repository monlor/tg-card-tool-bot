import re
import requests
from dotenv import load_dotenv
from cache import Cache
from rates import do_exchange
import os

load_dotenv()

# 汇率缓存24小时
cache = Cache(default_expiration=86400)

countries = [
    {"code": "HK", "group_symbol": ",", "currency": "HKD", "description": "🇭🇰 香港"},
    {"code": "US", "group_symbol": ",", "currency": "USD", "description": "🇺🇸 美国"},
    {"code": "GB", "group_symbol": ",", "currency": "GBP", "description": "🇬🇧 英国"},
    {"code": "SG", "group_symbol": ",", "currency": "SGD", "description": "🇸🇬 新加坡"},
    {"code": "DE", "group_symbol": ",", "currency": "EUR", "description": "🇩🇪 德国"},
    {"code": "PH", "group_symbol": ",", "currency": "PHP", "description": "🇵🇭 菲律宾"},
    {"code": "MY", "group_symbol": ",", "currency": "MYR", "description": "🇲🇾 马来西亚"},
    {"code": "TR", "group_symbol": ",", "currency": "TRY", "description": "🇹🇷 土耳其"},
    {"code": "NG", "group_symbol": ",", "currency": "NGN", "description": "🇳🇬 尼日利亚"},
    {"code": "VN", "group_symbol": ",", "currency": "VND", "description": "🇻🇳 越南"},
    {"code": "AR", "group_symbol": ",", "currency": "ARS", "description": "🇦🇷 阿根廷"},
    {"code": "JP", "group_symbol": ",", "currency": "JPY", "description": "🇯🇵 日本"},
    {"code": "PK", "group_symbol": ",", "currency": "PKR", "description": "🇵🇰 巴基斯坦"},
    {"code": "AU", "group_symbol": ",", "currency": "AUD", "description": "🇦🇺 澳大利亚"},
    {"code": "EG", "group_symbol": ",", "currency": "EGP", "description": "🇪🇬 埃及"}
]

MAIN_CURRENCY = os.getenv("MAIN_CURRENCY", "CNY")

def parse_primary_price(body):
    last_price = None
    regex = r'<p><strong>[^<]+</strong>(.*)'

    matches = re.findall(regex, body)

    last_price = matches[len(matches)-1]

    # 提取纯金额
    match = re.search(r'\d+(?:[,\.]\d+)?', last_price)
    if match:
        last_price = match.group()
    else:
        return "No amount", None

    if last_price is not None:
        return None, last_price
    else:
        return "No Premium plan", last_price

    return None, last_price


def get_netflix_data(country_code):
    url = f"https://help.netflix.com/zh-cn/node/24926/{country_code}"
    response = requests.get(url)

    if response.status_code == 200:
        # 处理成功响应
        data = response.text
        return None, data
    else:
        # 处理失败响应
        return f"请求失败，状态码：{response.status_code}", None

# 通过country_codes，返回所有价格
def list_netflix_price(countries):
    
    result = cache.get('netflix_prices')

    if result != None:
        return result

    result = []
    for country in countries:
        code = country['code']
        currency = country['currency']
        description = country['description']
        err, data = get_netflix_data(code)
        if err != None:
            result.append({ 'country_code': code , 'price': None, 'err': err, 'currency': currency, 'description': description })
            continue

        err, price = parse_primary_price(data)
        if err != None:
            result.append({ 'country_code': code , 'price': None, 'err': err, 'currency': currency, 'description': description })
            return

        price = price.replace(country['group_symbol'], '').replace(',', '.')

        price = float(price)

        result.append({ 'country_code': code , 'price': price, 'err': None, 'currency': currency, 'description': description })

    cache.set('netflix_prices', result)

    return result

def format_netflix_prices(currency, delay, exchange):
    prices = list_netflix_price(countries)
    
    # 判断是否做汇率换算
    if exchange:
        do_exchange(prices, currency)
        prices = sorted(prices, key=lambda x: x['target_price'])
        output = f'💡 Netflix 价格查询 {currency}\n\n'
    else:
        prices = sorted(prices, key=lambda x: x['country_code'])
        output = f'💡 Netflix 价格查询\n\n'

    for item in prices:
        if item['err'] != None:
            output += f"{item['description']} 👉 {item['err']}\n"
            continue
        if exchange:
            output += f"{item['description']} 👉 {item['target_price']:.2f} {currency}\n"
        else:
            output += f"{item['description']} 👉 {item['price']} {item['currency']}\n"
    
    if delay != None:
        output += f"\n👋 将在{delay}秒后删除消息..."

    return output


def netflix_input_parse(input_text, quote):
    usage_text = f'Usage: {input_text[0]} (货币)'

    currency = MAIN_CURRENCY
    
    if len(input_text) == 2:
        if not re.match(r'^[A-Za-z]{3}$', input_text[1]):
            return usage_text, None
        else:
            return None, input_text[1].upper()
    elif len(input_text) == 1:
        return None, currency
    else:
        return usage_text, None
