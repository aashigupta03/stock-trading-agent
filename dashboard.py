import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import ta
import json
import os
from datetime import datetime

# ── Page config ──────────────────────────────────────────────
st.set_page_config(
    page_title="AI Stock Trading Agent",
    page_icon="📈",
    layout="wide"
)

# ── Header ────────────────────────────────────────────────────
st.title("🤖 AI Stock Trading Agent Dashboard")
st.markdown("*Powered by Real-Time Market Data + AI Analysis*")
st.divider()

# ── Sidebar ───────────────────────────────────────────────────
st.sidebar.title("⚙️ Settings")
ticker = st.sidebar.text_input("Stock Ticker", value="AAPL").upper()
period = st.sidebar.selectbox("Time Period", ["1mo", "3mo", "6mo", "1y"], index=1)
run_agent = st.sidebar.button("🤖 Run AI Agent", type="primary")

st.sidebar.divider()
st.sidebar.markdown("### 📌 Quick Picks")
col1, col2 = st.sidebar.columns(2)
if col1.button("AAPL"): ticker = "AAPL"
if col2.button("NVDA"): ticker = "NVDA"
if col1.button("TSLA"): ticker = "TSLA"
if col2.button("MSFT"): ticker = "MSFT"

# ── Load Data ─────────────────────────────────────────────────
@st.cache_data(ttl=60)
def load_data(ticker, period):
    stock = yf.Ticker(ticker)
    hist = stock.history(period=period)
    info = stock.info
    return hist, info

try:
    with st.spinner(f"Loading {ticker} data..."):
        hist, info = load_data(ticker, period)

    # ── Top Metrics ───────────────────────────────────────────
    current_price = hist["Close"].iloc[-1]
    prev_price = hist["Close"].iloc[-2]
    change = current_price - prev_price
    change_pct = (change / prev_price) * 100

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("💰 Current Price", f"${current_price:.2f}",
                f"{change_pct:+.2f}%")
    col2.metric("📊 Volume", f"{hist['Volume'].iloc[-1]:,.0f}")
    col3.metric("🏢 Market Cap",
                f"${info.get('marketCap', 0)/1e9:.1f}B")
    col4.metric("📅 52W High",
                f"${info.get('fiftyTwoWeekHigh', 0):.2f}")

    st.divider()

    # ── Candlestick + Volume Chart ────────────────────────────
    st.subheader(f"📈 {ticker} Price Chart")

    fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                        row_heights=[0.7, 0.3],
                        subplot_titles=("Price (Candlestick)", "Volume"))

    fig.add_trace(go.Candlestick(
        x=hist.index, open=hist["Open"], high=hist["High"],
        low=hist["Low"], close=hist["Close"], name="Price"
    ), row=1, col=1)

    # Moving averages
    hist["MA20"] = hist["Close"].rolling(20).mean()
    hist["MA50"] = hist["Close"].rolling(50).mean()
    fig.add_trace(go.Scatter(x=hist.index, y=hist["MA20"],
                             name="MA20", line=dict(color="orange", width=1)), row=1, col=1)
    fig.add_trace(go.Scatter(x=hist.index, y=hist["MA50"],
                             name="MA50", line=dict(color="blue", width=1)), row=1, col=1)

    colors = ["green" if c >= o else "red"
              for c, o in zip(hist["Close"], hist["Open"])]
    fig.add_trace(go.Bar(x=hist.index, y=hist["Volume"],
                         marker_color=colors, name="Volume"), row=2, col=1)

    fig.update_layout(height=500, xaxis_rangeslider_visible=False,
                      template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

    # ── Technical Indicators ──────────────────────────────────
    st.subheader("📊 Technical Indicators")

    close = hist["Close"]
    rsi = ta.momentum.RSIIndicator(close).rsi()
    macd_obj = ta.trend.MACD(close)
    macd_line = macd_obj.macd()
    signal_line = macd_obj.macd_signal()

    col1, col2 = st.columns(2)

    with col1:
        fig_rsi = go.Figure()
        fig_rsi.add_trace(go.Scatter(x=hist.index, y=rsi,
                                     name="RSI", line=dict(color="purple")))
        fig_rsi.add_hline(y=70, line_dash="dash", line_color="red",
                          annotation_text="Overbought (70)")
        fig_rsi.add_hline(y=30, line_dash="dash", line_color="green",
                          annotation_text="Oversold (30)")
        fig_rsi.update_layout(title="RSI", height=300,
                              template="plotly_dark", yaxis=dict(range=[0, 100]))
        st.plotly_chart(fig_rsi, use_container_width=True)

        # RSI signal
        rsi_val = rsi.iloc[-1]
        if rsi_val > 70:
            st.error(f"🔴 RSI: {rsi_val:.1f} — Overbought (consider SELL)")
        elif rsi_val < 30:
            st.success(f"🟢 RSI: {rsi_val:.1f} — Oversold (consider BUY)")
        else:
            st.info(f"🔵 RSI: {rsi_val:.1f} — Neutral")

    with col2:
        fig_macd = go.Figure()
        fig_macd.add_trace(go.Scatter(x=hist.index, y=macd_line,
                                      name="MACD", line=dict(color="cyan")))
        fig_macd.add_trace(go.Scatter(x=hist.index, y=signal_line,
                                      name="Signal", line=dict(color="orange")))
        macd_hist = macd_line - signal_line
        fig_macd.add_trace(go.Bar(x=hist.index, y=macd_hist,
                                  name="Histogram",
                                  marker_color=["green" if v >= 0 else "red"
                                                for v in macd_hist]))
        fig_macd.update_layout(title="MACD", height=300,
                               template="plotly_dark")
        st.plotly_chart(fig_macd, use_container_width=True)

        macd_val = macd_line.iloc[-1]
        sig_val = signal_line.iloc[-1]
        if macd_val > sig_val:
            st.success("🟢 MACD above Signal — Bullish momentum")
        else:
            st.error("🔴 MACD below Signal — Bearish momentum")

    # ── AI Agent Decision ─────────────────────────────────────
    st.divider()
    st.subheader("🤖 AI Agent Decision")

    if run_agent:
        with st.spinner("🤖 AI Agent is analyzing the stock..."):
            try:
                from agent import run_agent as get_decision
                decision = get_decision(ticker)

                if "BUY" in decision.upper():
                    st.success(f"### ✅ RECOMMENDATION: BUY")
                elif "SELL" in decision.upper():
                    st.error(f"### ❌ RECOMMENDATION: SELL")
                else:
                    st.warning(f"### ⏸️ RECOMMENDATION: HOLD")

                st.markdown("**Full AI Analysis:**")
                st.write(decision)

            except Exception as e:
                st.error(f"Agent error: {e}")
    else:
        st.info("👈 Click **'Run AI Agent'** in the sidebar to get an AI recommendation for this stock!")

    # ── Trade History ─────────────────────────────────────────
    st.divider()
    st.subheader("📜 Trade History Log")

    if os.path.exists("trade_log.json"):
        with open("trade_log.json") as f:
            history = json.load(f)

        if history:
            df = pd.DataFrame(history)
            df["timestamp"] = pd.to_datetime(df["timestamp"])
            df["timestamp"] = df["timestamp"].dt.strftime("%Y-%m-%d %H:%M")
            df = df.iloc[::-1].reset_index(drop=True)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No trades logged yet.")
    else:
        st.info("No trade history found. Run the AI agent to generate trades!")

except Exception as e:
    st.error(f"❌ Could not load data for **{ticker}**. Check the ticker symbol.")
    st.exception(e)