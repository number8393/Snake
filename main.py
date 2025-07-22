import requests
import json
import time
import random
from datetime import datetime

# === Настройки ===
ALPHA_KEY = "QB0A7R9NHGX8COY2"
NEWS_API_KEY = "YOUR_NEWS_API_KEY"  # заменишь на свой
TG_TOKEN = "8094752756:AAFUdZn4XFlHiZOtV-TXzMOhYFlXKCFVoEs"
TG_CHAT_ID = "5556108366"

# === Валютные пары ===
symbols = {
    "EUR/USD": "EURUSD",
    "GBP/USD": "GBPUSD",
    "USD/JPY": "USDJPY",
    "USD/CHF": "USDCHF",
    "AUD/USD": "AUDUSD",
    "NZD/USD": "NZDUSD",
    "USD/CAD": "USDCAD"
}

# === Функции ===

def fetch_price(symbol):
    url = f"https://www.alphavantage.co/query?function=CURRENCY_EXCHANGE_RATE&from_currency={symbol[:3]}&to_currency={symbol[3:]}&apikey={ALPHA_KEY}"
    res = requests.get(url).json()
    return float(res["Realtime Currency Exchange Rate"]["5. Exchange Rate"])

def fetch_news():
    try:
        res = requests.get(f"https://newsapi.org/v2/top-headlines?category=business&language=en&apiKey={NEWS_API_KEY}")
        data = res.json()
        return [a["title"] for a in data["articles"][:3]]
    except:
        return []

def load_memory():
    try:
        with open("memory.json", "r") as f:
            return json.load(f)
    except:
        return {}

def save_memory(memory):
    with open("memory.json", "w") as f:
        json.dump(memory, f)

def smart_logic(price, symbol, memory):
    mem = memory.get(symbol, {"correct": 1, "wrong": 1})
    confidence = round((mem["correct"] / (mem["correct"] + mem["wrong"])) * 100, 2)

    if price > 1.1:
        return "Buy", confidence + random.randint(0, 5)
    elif price < 0.9:
        return "Sell", confidence + random.randint(0, 5)
    else:
        return "Hold", confidence

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": TG_CHAT_ID, "text": msg})

# === Основной цикл ===
while True:
    memory = load_memory()
    now = datetime.now().strftime("%H:%M:%S")
    news = fetch_news()

    for name, code in symbols.items():
        try:
            price = fetch_price(code)
            action, confidence = smart_logic(price, code, memory)

            if action == "Hold":
                msg = f"📉 {name} | {now}\nЦена: {price:.4f}\n❗ Нет чёткого сигнала\n🗞 Альтернатива: ждать\n🧠 Новости: {'; '.join(news)}"
            else:
                msg = f"📈 {name} | {now}\nСигнал: {action}\nЦена: {price:.4f}\nУверенность: {confidence}%\n🧠 Новости: {'; '.join(news)}"

            send_telegram(msg)
        except Exception as e:
            send_telegram(f"❌ Ошибка {name}: {str(e)}")

    time.sleep(900)  # каждые 15 минут
