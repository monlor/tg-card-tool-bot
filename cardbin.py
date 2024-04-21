import os
import requests
from dotenv import load_dotenv
import datetime

load_dotenv()

BINLIST_API = "https://lookup.binlist.net/{}"
API_LAYER_API = "https://api.apilayer.com/bincheck/{}"
HANDYAPI_API = "https://data.handyapi.com/bin/{}"
API_LAYER_KEY = os.getenv("API_LAYER_KEY")
DELETE_DELAY = int(os.getenv("DELETE_DELAY", 60))

def get_bin_from_binlist(quote):
    api_url = BINLIST_API.format(quote)
    headers = {
        "Accept-Version": "3"
    }
    raw_data = []
    try:
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()  # 检查请求是否成功，如果不成功，抛出异常
        raw_data = response.json()  # 返回JSON解析后的数据
    except requests.RequestException as e:
        print(f"请求错误: {e}")
        return None
    
    if not raw_data:
        return None

    return {
        "prepaid": raw_data.get("prepaid", None),
        "scheme": raw_data.get("scheme", "未知"),
        "type": raw_data.get("type", "未知"),
        "country_name": raw_data.get("country", {}).get("name", "未知"),
        "country_currency": raw_data.get("country", {}).get("currency", ""),
        "country_emoji": raw_data.get("country", {}).get("emoji", ""),
        "bank_name": raw_data.get("bank", {}).get("name", "未知")
    }

def get_bin_from_handyapi(quote):
    api_url = HANDYAPI_API.format(quote)
    raw_data = []
    try:
        response = requests.get(api_url)
        response.raise_for_status()  # 检查请求是否成功，如果不成功，抛出异常
        raw_data = response.json()  # 返回JSON解析后的数据
    except requests.RequestException as e:
        print(f"请求错误: {e}")
        return None
    
    if not raw_data:
        return None

    return {
        "prepaid": None,
        "scheme": raw_data.get("Scheme", "未知"),
        "type": raw_data.get("Type", "未知"),
        "country_name": raw_data.get("Country", {}).get("Name", "未知"),
        "country_currency": "未知",
        "country_emoji": "",
        "bank_name": raw_data.get("Issuer", "未知")
    }

def get_bin_from_apilayer(quote):
    api_url = API_LAYER_API.format(quote)
    headers = {
        "apikey": API_LAYER_KEY
    }
    raw_data = []
    try:
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()  # 检查请求是否成功，如果不成功，抛出异常
        raw_data = response.json()  # 返回JSON解析后的数据
    except requests.RequestException as e:
        print(f"请求错误: {e}")
        return None

    if not raw_data:
        return None

    return {
        "prepaid": None,
        "scheme": raw_data.get("scheme", "未知"),
        "type": raw_data.get("type", "未知"),
        "country_name": raw_data.get("country", "位置"),
        "country_currency": "未知",
        "country_emoji": "",
        "bank_name": raw_data.get("bank_name", "未知")
    }

def get_bin(quote):
    res = get_bin_from_binlist(quote)

    if (res == None):
        res = get_bin_from_handyapi(quote)
        if (res == None) and API_LAYER_KEY:
            res = get_bin_from_apilayer(quote)

    return res

def format_bin_response(quote, data):
    if not data:
        return "获取数据失败或数据为空。"

    output = "💡 卡BIN查询\n\n"
    output += f"✅ 卡片BIN: {quote}\n"
    output += f"💳 支付体系: {data['scheme']}\n"
    output += f"🏦 卡片类型: {data['type']}\n"
    output += f"💵 卡片币种: {data['country_currency']}\n"
    output += f"🌍 发行国家: {data['country_emoji'] } {data['country_name']}\n"
    output += f"🏢 银行名称: {data['bank_name']}\n"

    if data['prepaid'] != None:
        output += f"\n📲 是否预付卡：{'✅' if data['prepaid'] else '❌'}\n"

    output += f"\n👋 将在{DELETE_DELAY}秒后删除消息..."
    
    return output