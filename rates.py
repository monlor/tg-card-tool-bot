import os
import requests
from dotenv import load_dotenv
import datetime

load_dotenv()

EXCHANGERATE_API_KEY = os.getenv("EXCHANGERATE_API_KEY")

ECONOMIA_API = "https://economia.awesomeapi.com.br/json/daily/{}-{}/{}"

EXCHANGERATE_API = "https://v6.exchangerate-api.com/v6/{}/pair/{}/{}"

def format_timestamp(t):
    dt = datetime.datetime.fromtimestamp(int(t))
    return dt.strftime('%Y-%m-%d')

def get_rates_from_economia(source, target):
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

def get_rates(source, target):
    rate = get_rates_from_economia(source, target)

    if (rate == None or rate == "") and EXCHANGERATE_API_KEY:
        rate = get_rates_from_exchangerate(source, target)
    
    return rate

def format_rate_response(source, target, amount, delay, rate):
    response = "💡 汇率查询\n"
    response += f"\n💹 汇率查询: 1 {source} = {rate} {target}\n"

    equiv_amount = amount * rate
    response += f"\n💰 货币换算: {amount} {source} = {equiv_amount:.2f} {target}\n"

    response += f"\n👋 将在{delay}秒后删除消息..."

    return response