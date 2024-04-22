import os
import requests
from dotenv import load_dotenv
import datetime

load_dotenv()

RATES_API = "https://economia.awesomeapi.com.br/json/daily/{}-{}/{}"

def format_timestamp(t):
    dt = datetime.datetime.fromtimestamp(int(t))
    return dt.strftime('%Y-%m-%d')

def get_rates(source, target, days):
    api_url = RATES_API.format(source, target, days)
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

def format_rate_response(source, target, amount, delay, rates):
    response = "💡 汇率查询\n"
    response += f"\n💹 {source}对{target}的汇率:\n"
    for rate in rates:
        response += f"{rate['date']}: 1 {source} = {rate['rate']} {target}\n"

    response += f"\n💰 {amount} {target} 的价值:\n"
    for rate in rates:
        equiv_amount = amount / rate['rate']
        response += f"{rate['date']}: {equiv_amount:.2f} {source}\n"

    response += f"\n👋 将在{delay}秒后删除消息..."

    return response