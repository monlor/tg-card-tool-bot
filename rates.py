import os
import requests
from dotenv import load_dotenv
import datetime

load_dotenv()

RATES_API = "https://economia.awesomeapi.com.br/json/daily/{}-{}/{}"
QUERY_DAYS = int(os.getenv("QUERY_DAYS", 5))
MAIN_CURRENCY = os.getenv("MAIN_CURRENCY", "USD")
DELETE_DELAY = int(os.getenv("DELETE_DELAY", 60))

def format_timestamp(t):
    dt = datetime.datetime.fromtimestamp(int(t))
    return dt.strftime('%Y-%m-%d')

def get_rates(quote):
    api_url = RATES_API.format(MAIN_CURRENCY, quote, QUERY_DAYS)
    response = requests.get(api_url)
    data = response.json()
    
    rates = []
    for entry in data:
        rates.append({
            "date": format_timestamp(entry["timestamp"]),
            # bid是卖出价，ask时买入价
            "rate": float(entry["bid"])
        })
    
    return rates

def format_rate_response(quote, amount, rates):
    response = "💡 汇率查询\n"
    response += f"\n💹 最近{QUERY_DAYS}天{MAIN_CURRENCY}对{quote}的汇率:\n"
    for rate in rates:
        response += f"{rate['date']}: 1 {MAIN_CURRENCY} = {rate['rate']} {quote}\n"

    response += f"\n💰 最近{QUERY_DAYS}天 {amount} {quote} 的价值:\n"
    for rate in rates:
        equiv_amount = amount / rate['rate']
        response += f"{rate['date']}: {equiv_amount:.2f} {MAIN_CURRENCY}\n"

    response += f"\n👋 将在{DELETE_DELAY}秒后删除消息..."

    return response