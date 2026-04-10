from agent import run_agent
from memory import log_decision, get_history
from rich.console import Console
from rich.panel import Panel
import time

console = Console()

if __name__ == "__main__":
    console.print(Panel("🚀 AI Stock Trading Agent", style="bold green"))

    tickers = ["AAPL"]  # Just 1 stock for now

    for ticker in tickers:
        console.rule(f"[bold blue]{ticker}")
        decision = run_agent(ticker)
        log_decision(ticker, decision)
        time.sleep(3)  # Wait 3 seconds between stocks

    console.print("\n📜 Trade History:")
    for entry in get_history()[-5:]:
        console.print(f"  [{entry['timestamp']}] {entry['ticker']}: {entry['decision'][:80]}...")