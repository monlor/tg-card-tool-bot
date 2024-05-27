import re
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from cache import Cache
from rates import do_exchange, get_rates
import os

load_dotenv()

# 汇率缓存24小时
cache = Cache(default_expiration=86400)

# 金额分组符号用.的国家
country_codes = [ 'VN', 'TR', 'FR', 'BE', 'NL', 'ES', 'PT', 'AT', 'SK', 'SI', 'EE', 'LV', 'LT', 'FI', 'GR', 'HR', 'HU', 'BG', 'MT', 'LU', 'CY', 'CZ', 'RO', 'PL', 'SE', 'DK', 'IE', 'IT', 'DE' ]

# 默认显示国家列表
default_country_codes = [ 'US', 'HK', 'CN', 'PH', 'TR', 'NG', 'MY' ]

country_infos = {
    'cn': { 'flag': '🇨🇳', 'name': '中国大陆', 'currency': 'CNY' },
    'us': { 'flag': '🇺🇸', 'name': '美国', 'currency': 'USD' },
    'jp': { 'flag': '🇯🇵', 'name': '日本', 'currency': 'JPY' },
    'kr': { 'flag': '🇰🇷', 'name': '韩国', 'currency': 'KRW' },
    'hk': { 'flag': '🇭🇰', 'name': '香港', 'currency': 'HKD' },
    'tw': { 'flag': '🇨🇳', 'name': '台湾', 'currency': 'TWD' },
    'sg': { 'flag': '🇸🇬', 'name': '新加坡', 'currency': 'SGD' },
    'my': { 'flag': '🇲🇾', 'name': '马来西亚', 'currency': 'MYR' },
    'th': { 'flag': '🇹🇭', 'name': '泰国', 'currency': 'THB' },
    'vn': { 'flag': '🇻🇳', 'name': '越南', 'currency': 'VND' },
    'ph': { 'flag': '🇵🇭', 'name': '菲律宾', 'currency': 'PHP' },
    'id': { 'flag': '🇮🇩', 'name': '印度尼西亚', 'currency': 'IDR' },
    'ru': { 'flag': '🇷🇺', 'name': '俄罗斯', 'currency': 'RUB' },
    'gb': { 'flag': '🇬🇧', 'name': '英国', 'currency': 'GBP' },
    'fr': { 'flag': '🇫🇷', 'name': '法国', 'currency': 'EUR' },
    'de': { 'flag': '🇩🇪', 'name': '德国', 'currency': 'EUR' },
    'it': { 'flag': '🇮🇹', 'name': '意大利', 'currency': 'EUR' },
    'es': { 'flag': '🇪🇸', 'name': '西班牙', 'currency': 'EUR' },
    'pt': { 'flag': '🇵🇹', 'name': '葡萄牙', 'currency': 'EUR' },
    'nl': { 'flag': '🇳🇱', 'name': '荷兰', 'currency': 'EUR' },
    'be': { 'flag': '🇧🇪', 'name': '比利时', 'currency': 'EUR' },
    'at': { 'flag': '🇦🇹', 'name': '奥地利', 'currency': 'EUR' },
    'fi': { 'flag': '🇫🇮', 'name': '芬兰', 'currency': 'EUR' },
    'ie': { 'flag': '🇮🇪', 'name': '爱尔兰', 'currency': 'EUR' },
    'ng': { 'flag': '🇳🇬', 'name': '尼日利亚', 'currency': 'NGN' },
    'tr': { 'flag': '🇹🇷', 'name': '土耳其', 'currency': 'TRY' },
}

MAIN_CURRENCY = os.getenv("MAIN_CURRENCY", "CNY")

def parse_price(country_code, price):
    match = re.search(r'\d+(?:[,\.]\d+)?', price)
    if match:
        price = match.group()
    else:
        return 'No amount', 0
    if country_code in country_codes:
        price = price.replace('.', '').replace(',', '.')
    else:
        price = price.replace(',', '')
    return None, price

def get_country_info(country_code):
    res = cache.get(country_code)
    if res != None:
        return None, res['flag'], res['name'], res['currency']

    url = f'https://restcountries.com/v3/alpha/{country_code}'

    try:
        response = requests.get(url, timeout=1)
        print(f"请求国家信息 {url}")
        if response.status_code == 200:
            # 处理成功响应
            data = response.json()
            flag = data[0]['flag']
            name = None
            currency = next(iter(data[0]['currencies']))
            if 'zho' in data[0]['languages']:
                name = data[0]['name']['nativeName']['zho']['common']
            else:
                name = data[0]['translations']['zho']['common']
            cache.set(country_code, { 'flag': flag, 'name': name, 'currency': currency })
            return None, flag, name, currency
        else:
            # 处理失败响应
            return f"国家信息请求失败，状态码：{response.status_code}", None, None, None
    except requests.RequestException as e:
        # 从本地数据中获取
        country_code = country_code.lower()
        if country_code in country_infos:
            return None, country_infos[country_code]['flag'], country_infos[country_code]['name'], country_infos[country_code]['currency']
        else:
            return f"国家信息获取失败，错误：{e}", None, None, None

def get_data(currency, country_code, app_name, app_id):
    cache_key = f'{currency}-{country_code}-{app_id}'
    res = cache.get(cache_key)
    app_price = cache.get(f'{cache_key}-app')
    if res != None:
        return None, res, app_price
    url = f"https://apps.apple.com/{country_code}/app/{app_name}/{app_id}"
    # Send a GET request to the URL
    response = requests.get(url)

    data = None
    if response.status_code == 200:
        # 处理成功响应
        data = response.content
    else:
        # 处理失败响应
        return f"AppStore请求失败，状态码：{response.status_code}，该地区可能不支持查询！", None, None

    # Parse the HTML content
    soup = BeautifulSoup(data, "html.parser")

    # Find all the list items with prices
    price_items = soup.select("li.list-with-numbers__item")

    # Extract the service name and price from each list item
    services = []
    for item in price_items:
        title = item.select_one("span.list-with-numbers__item__title span.truncate-single-line").text.strip()
        price = item.select_one("span.list-with-numbers__item__price").text.strip()
        err, price = parse_price(country_code, price)
        services.append({"name": title, "price": float(price), "err": err, 'currency': currency})

    # 获取应用价格
    app_price_text = None
    price_element = soup.find('li', class_='inline-list__item inline-list__item--bulleted app-header__list__item--price')
    if price_element != None:
        err, app_price_text = parse_price(country_code, price_element.text)

    if app_price_text != None:
        app_price = float(app_price_text)
        cache.set(f'{cache_key}-app', app_price)

    cache.set(cache_key, services)

    return None, services, app_price

async def format_appstore_prices_one(main_currency, country_code, app_name, app_id, delay, exchange):
    return await format_appstore_prices(main_currency, [country_code], app_name, app_id, delay, exchange)

async def format_appstore_prices_all(main_currency, app_name, app_id, delay, exchange):
    return await format_appstore_prices(main_currency, default_country_codes, app_name, app_id, delay, exchange)

async def format_appstore_prices(main_currency, country_codes, app_name, app_id, delay, exchange):

    output = f'💡 AppStore 价格查询\n'

    for country_code in country_codes:

        output += '\n------\n\n'

        err, flag, country_name, currency = get_country_info(country_code)
        if err != None:
            return err

        output += f'🌍 地区：{flag} {country_name}\n\n'

        err, prices, app_price = get_data(currency, country_code, app_name, app_id)

        if err != None:
            output += f'❌ {err}\n'
        else:
            # 判断是否做汇率换算
            if exchange:
                await do_exchange(prices, main_currency)
                rate = await get_rates(currency, main_currency)
                if rate != None:
                    app_price = app_price * rate
                else:
                    app_price = None
            else:
                main_currency = currency
            
            if app_price != None:
                output += f'🏷️ 应用购买价格 👉 {app_price:.2f} {main_currency}\n\n'
            
            if len(prices) == 0:
                output += f'😄 这个App没有内购信息！\n'

            for item in prices:
                if item['err'] != None:
                    output += f"📚 {item['name']} 👉 {item['err']}\n"
                    continue
                if exchange:
                    output += f"📚 {item['name']} 👉 {item['target_price']:.2f} {main_currency}\n"
                else:
                    output += f"📚 {item['name']} 👉 {item['price']} {main_currency}\n"
    
    if delay != None:
        output += f"\n👋 将在{delay}秒后删除消息..."

    return output

def is_appstore_url(url):
    pattern = r"https://apps\.apple\.com/(?P<country_code>[^/]+)/app/(?P<app_name>[^/]+)/(?P<app_id>[^/?]+)"

    # 进行匹配
    match = re.match(pattern, url)

    if match:
        # 提取匹配到的值
        country_code = match.group("country_code")
        app_name = match.group("app_name")
        app_id = match.group("app_id")
        return country_code, app_name, app_id
    else:
        return None, None, None

def is_currency(q):
    return re.match(r'^[A-Za-z]{3}$', q)

def is_country_code(q):
    return re.match(r'^[A-Za-z]{2}$', q)

def extract_links_from_url(q):
    # 定义匹配URL的正则表达式模式
    pattern = r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"

    # 使用findall函数从URL中提取链接
    links = re.findall(pattern, q)

    if len(links) > 0:
        return links[0]
    return None

async def appstore_input_parse(input_text, quote):
    usage_text = f'Usage: {input_text[0]} [appstore url] (地区代码，如hk) (货币)'

    currency = MAIN_CURRENCY

    url = None
    country_code = None

    if quote != None:
        url = extract_links_from_url(quote)
        if len(input_text) >= 2:
            if is_country_code(input_text[1]):
                country_code = input_text[1]
            else:
                return usage_text, None, None, None, None
        if len(input_text) == 3:
            if is_currency(input_text[2]):
                currency = input_text[2]
            else:
                return usage_text, None, None, None, None
        
        if len(input_text) > 3:
            return usage_text, None, None, None, None
    else:
        if len(input_text) == 1:
            return usage_text, None, None, None, None
        url = input_text[1]
        if len(input_text) >= 2:
            url = input_text[1]
        if len(input_text) >= 3:
            if is_country_code(input_text[2]):
                country_code = input_text[2]
            else:
                return usage_text, None, None, None, None
        if len(input_text) == 4:
            if is_currency(input_text[3]):
                currency = input_text[3]
            else:
                return usage_text, None, None, None, None
        
        if len(input_text) > 4:
            return usage_text, None, None, None, None
        
    if url == None:
        return usage_text, None, None, None, None

    country_code_ori, app_name, app_id = is_appstore_url(url)

    if country_code_ori == None or app_name == None or app_id == None:
        return usage_text, None, None, None, None

    if country_code == None:
        country_code = country_code_ori

    return None, currency.upper(), country_code.upper(), app_name, app_id


async def appstorea_input_parse(input_text, quote):
    usage_text = f'Usage: {input_text[0]} [appstore url] (货币)'

    currency = MAIN_CURRENCY

    url = None

    if quote != None:
        url = extract_links_from_url(quote)
        if len(input_text) == 2:
            if is_currency(input_text[1]):
                currency = input_text[1]
            else:
                return usage_text, None, None, None, None
        
        if len(input_text) > 2:
            return usage_text, None, None, None, None
    else:
        if len(input_text) == 1:
            return usage_text, None, None, None, None
        url = input_text[1]
        if len(input_text) >= 2:
            url = input_text[1]
        if len(input_text) == 3:
            if is_currency(input_text[2]):
                currency = input_text[2]
            else:
                return usage_text, None, None, None, None
        
        if len(input_text) > 3:
            return usage_text, None, None, None, None
        
    if url == None:
        return usage_text, None, None, None, None

    country_code, app_name, app_id = is_appstore_url(url)

    if country_code == None or app_name == None or app_id == None:
        return usage_text, None, None, None, None

    return None, currency.upper(), country_code.upper(), app_name, app_id

