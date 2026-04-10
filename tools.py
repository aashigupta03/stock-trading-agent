import yfinance as yf
import ta

def get_stock_price(ticker: str) -> dict:
    stock = yf.Ticker(ticker)
    hist = stock.history(period="1d")
    info = stock.info
    return {
        "ticker": ticker,
        "current_price": round(hist["Close"].iloc[-1], 2),
        "volume": int(hist["Volume"].iloc[-1]),
        "market_cap": info.get("marketCap", "N/A"),
    }

def get_technical_indicators(ticker: str) -> dict:
    hist = yf.Ticker(ticker).history(period="3mo")
    close = hist["Close"]
    rsi = ta.momentum.RSIIndicator(close).rsi().iloc[-1]
    macd_obj = ta.trend.MACD(close)
    macd = macd_obj.macd().iloc[-1]
    signal = macd_obj.macd_signal().iloc[-1]
    ma50 = close.rolling(50).mean().iloc[-1]
    ma200 = close.rolling(200).mean().iloc[-1]
    return {
        "ticker": ticker,
        "RSI": round(rsi, 2),
        "MACD": round(macd, 4),
        "MACD_signal": round(signal, 4),
        "MA_50": round(ma50, 2),
        "MA_200": round(ma200, 2),
    }

def get_news_sentiment(ticker: str) -> dict:
    stock = yf.Ticker(ticker)
    news = stock.news[:3]
    headlines = [n.get("content", {}).get("title", "") for n in news]
    return {"ticker": ticker, "headlines": headlines}

TOOLS = [
    {
        "name": "get_stock_price",
        "description": "Get the current stock price and volume for a ticker.",
        "input_schema": {
            "type": "object",
            "properties": {"ticker": {"type": "string", "description": "Stock ticker e.g. AAPL"}},
            "required": ["ticker"]
        }
    },
    {
        "name": "get_technical_indicators",
        "description": "Get RSI, MACD, and moving averages for a stock.",
        "input_schema": {
            "type": "object",
            "properties": {"ticker": {"type": "string"}},
            "required": ["ticker"]
        }
    },
    {
        "name": "get_news_sentiment",
        "description": "Get recent news headlines for a stock ticker.",
        "input_schema": {
            "type": "object",
            "properties": {"ticker": {"type": "string"}},
            "required": ["ticker"]
        }
    }
]

TOOL_MAP = {
    "get_stock_price": get_stock_price,
    "get_technical_indicators": get_technical_indicators,
    "get_news_sentiment": get_news_sentiment,
}