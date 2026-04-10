import json
import urllib.request
from tools import TOOL_MAP

import os
API_KEY = os.environ.get("OPENROUTER_API_KEY", "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")


def run_agent(ticker: str) -> str:
    print(f"\n🤖 Agent analyzing {ticker}...\n")

    print("🔧 Getting stock price...")
    price_data = TOOL_MAP["get_stock_price"](ticker)
    print(f"📊 {price_data}\n")

    print("🔧 Getting technical indicators...")
    indicators = TOOL_MAP["get_technical_indicators"](ticker)
    print(f"📊 {indicators}\n")

    print("🔧 Getting news...")
    news = TOOL_MAP["get_news_sentiment"](ticker)
    print(f"📊 {news}\n")

    prompt = f"""You are a stock trading analyst. Based on this data, give a BUY, SELL or HOLD recommendation with reasoning.

Stock: {ticker}
Price Data: {json.dumps(price_data)}
Technical Indicators: {json.dumps(indicators)}
News Headlines: {json.dumps(news)}

Give your recommendation and confidence level 1-10."""

    data = json.dumps({
        "model": "google/gemma-3-4b-it:free",
        "messages": [{"role": "user", "content": prompt}]
    }).encode("utf-8")

    req = urllib.request.Request(
        "https://openrouter.ai/api/v1/chat/completions",
        data=data,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {API_KEY}"
        },
        method="POST"
    )

    import time
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req) as resp:
                result = json.loads(resp.read())
                answer = result["choices"][0]["message"]["content"]
                print(f"💬 Agent Decision:\n{answer}")
                return answer
        except Exception as e:
            print(f"⏳ Rate limited, waiting 30 seconds... (attempt {attempt+1}/3)")
            time.sleep(30)
    return "Could not get decision after 3 attempts"