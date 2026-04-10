import json
import os
from datetime import datetime

LOG_FILE = "trade_log.json"

def log_decision(ticker: str, decision: str):
    log = []
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE) as f:
            log = json.load(f)
    log.append({
        "timestamp": datetime.now().isoformat(),
        "ticker": ticker,
        "decision": decision,
    })
    with open(LOG_FILE, "w") as f:
        json.dump(log, f, indent=2)
    print(f"✅ Decision logged!")

def get_history():
    if not os.path.exists(LOG_FILE):
        return []
    with open(LOG_FILE) as f:
        return json.load(f)