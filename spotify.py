import re
import requests
from dotenv import load_dotenv
from cache import Cache
from rates import get_rates
import os

load_dotenv()

# 汇率缓存3小时
cache = Cache(default_expiration=86400)

countries = [
    {"code": "HK", "group_symbol": ",", "currency": "HKD", "description": "🇭🇰 香港"},
    {"code": "US", "group_symbol": ",", "currency": "USD", "description": "🇺🇸 美国"},
    {"code": "UK", "group_symbol": ",", "currency": "GBP", "description": "🇬🇧 英国"},
    {"code": "SG", "group_symbol": ",", "currency": "SGD", "description": "🇸🇬 新加坡"},
    {"code": "DE", "group_symbol": ".", "currency": "EUR", "description": "🇩🇪 德国"},
    {"code": "PH", "group_symbol": ",", "currency": "PHP", "description": "🇵🇭 菲律宾"},
    {"code": "MY", "group_symbol": ",", "currency": "MYR", "description": "🇲🇾 马来西亚"},
    {"code": "TR", "group_symbol": ".", "currency": "TRY", "description": "🇹🇷 土耳其"},
    {"code": "NG", "group_symbol": ",", "currency": "NGN", "description": "🇳🇬 尼日利亚"},
    {"code": "VN", "group_symbol": ".", "currency": "VND", "description": "🇻🇳 越南"},
    {"code": "AR", "group_symbol": ".", "currency": "ARS", "description": "🇦🇷 阿根廷"},
    {"code": "JP", "group_symbol": ",", "currency": "JPY", "description": "🇯🇵 日本"},
    {"code": "PK", "group_symbol": ",", "currency": "PKR", "description": "🇵🇰 巴基斯坦"},
    {"code": "AU", "group_symbol": ",", "currency": "AUD", "description": "🇦🇺 澳大利亚"}
]

MAIN_CURRENCY = os.getenv("MAIN_CURRENCY", "USD")

def parse_primary_price(body):
    last_price = None
    regex = r'"primaryPriceDescription"\s*:\s*"([^"]+)"'

    matches = re.findall(regex, body)

    last_price = matches[len(matches)-1]
    if "Free" in last_price:
        last_price = matches[len(matches)-2]

    # 提取纯金额
    match = re.search(r'\d+(?:[,\.]\d+)?', last_price)
    if match:
        last_price = match.group()
    else:
        return "No amount", None

    if last_price is not None:
        return None, last_price
    else:
        return "No family plan", last_price

    return None, last_price


def get_spotify_data(country_code):
    url = f"https://www.spotify.com/{country_code}/premium/"
    response = requests.get(url)

    if response.status_code == 200:
        # 处理成功响应
        data = response.text
        return None, data
    else:
        # 处理失败响应
        return f"请求失败，状态码：{response.status_code}", None

# 通过country_codes，返回所有价格
def list_spotify_price(countries):
    
    result = cache.get('spotify_prices')

    if result != None:
        return result

    result = []
    for country in countries:
        code = country['code']
        currency = country['currency']
        description = country['description']
        err, data = get_spotify_data(code)
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

    cache.set('spotify_prices', result)

    return result


def format_spotify_prices(currency, delay):
    prices = list_spotify_price(countries)
    output = f'💡 Spotify 价格查询 {currency}\n\n'

    for item in prices:
        if item['err'] != None:
            continue
        target_price = 0
        price = item['price']
        description = item['description']
        if price != None:
            if item['currency'] != currency:
                rate = get_rates(item['currency'], currency)
                if rate != None:
                    target_price = price * rate
            else:
                target_price = price
        item['target_price'] = target_price

    prices = sorted(prices, key=lambda x: x['target_price'])

    for item in prices:
        if item['err'] != None:
            output += f"{item['description']} {item['err']}"
            continue
        output += f"{item['description']} 💰 {item['price']} {item['currency']} 👉 {item['target_price']:.2f} {currency}\n"
    
    if delay != None:
        output += f"\n👋 将在{delay}秒后删除消息..."

    return output


def spotify_input_parse(input_text, quote):
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
