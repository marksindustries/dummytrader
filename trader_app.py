import json
import math
import statistics
import urllib.error
import urllib.request
from datetime import datetime
from tkinter import Tk, Label, Entry, Button, Text, END

# Simple portfolio templates by risk appetite
PORTFOLIO_TEMPLATES = {
    "low": ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS"],
    "medium": ["INFY.NS", "ICICIBANK.NS", "ITC.NS"],
    "high": ["ADANIPOWER.NS", "ZOMATO.NS", "PAYTM.NS"],
}


def fetch_history(symbol: str, months: int = 6):
    """Fetch historical daily close prices for the symbol from Yahoo Finance.

    Returns list of (timestamp, close) tuples. If fetching fails, an empty list
    is returned.
    """
    url = (
        f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?range={months}mo&interval=1d"
    )
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            data = json.load(resp)
        result = data["chart"]["result"][0]
        timestamps = result["timestamp"]
        closes = result["indicators"]["adjclose"][0]["adjclose"]
        return list(zip(timestamps, closes))
    except Exception:
        return []


def fetch_pe_ratio(symbol: str):
    """Fetch trailing P/E ratio for the symbol. Returns None on failure."""
    url = (
        "https://query1.finance.yahoo.com/v10/finance/quoteSummary/"
        f"{symbol}?modules=summaryDetail"
    )
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            data = json.load(resp)
        summary = data["quoteSummary"]["result"][0]["summaryDetail"]
        pe = summary.get("trailingPE", {}).get("raw")
        return pe
    except Exception:
        return None


def moving_average(values, window):
    if len(values) < window:
        return [math.nan] * len(values)
    ma = []
    for i in range(len(values)):
        if i + 1 < window:
            ma.append(math.nan)
        else:
            ma.append(statistics.mean(values[i + 1 - window : i + 1]))
    return ma


def analyze_stock(symbol: str, risk: str, investment: float):
    history = fetch_history(symbol)
    if not history:
        return {
            "decision": "Data unavailable",
            "when": "",
            "portfolio": {},
        }
    dates, closes = zip(*history)
    ma5 = moving_average(closes, 5)
    ma20 = moving_average(closes, 20)
    latest_close = closes[-1]
    latest_ma5 = ma5[-1]
    latest_ma20 = ma20[-1]

    # Technical signal
    tech_signal = "buy" if latest_ma5 > latest_ma20 else "sell"

    # Fundamental signal
    pe = fetch_pe_ratio(symbol)
    fundamental = "undervalued" if pe is not None and pe < 25 else "overvalued"

    if tech_signal == "buy" and fundamental == "undervalued":
        decision = "BUY"
    elif tech_signal == "sell" or fundamental == "overvalued":
        decision = "SELL"
    else:
        decision = "HOLD"

    # Estimate when a crossover might happen
    diff_series = [m20 - m5 for m5, m20 in zip(ma5, ma20)]
    recent_diff = diff_series[-5:]
    if len(recent_diff) >= 2:
        changes = [j - i for i, j in zip(recent_diff[:-1], recent_diff[1:])]
        slope = statistics.mean(changes)
    else:
        slope = 0
    diff_now = diff_series[-1]
    when_msg = ""
    if slope != 0:
        days_to_cross = abs(diff_now / slope)
        if diff_now > 0 and slope < 0:
            when_msg = f"Possible bullish crossover in ~{int(days_to_cross)} days"
        elif diff_now < 0 and slope > 0:
            when_msg = f"Possible bearish crossover in ~{int(days_to_cross)} days"

    # Build portfolio
    template = PORTFOLIO_TEMPLATES.get(risk.lower(), PORTFOLIO_TEMPLATES["medium"])
    allocation = investment / len(template) if template else 0
    portfolio = {s: round(allocation, 2) for s in template}

    return {"decision": decision, "when": when_msg, "portfolio": portfolio}


def build_gui():
    root = Tk()
    root.title("Dummy Trader")

    Label(root, text="Stock Symbol").grid(row=0, column=0)
    symbol_entry = Entry(root)
    symbol_entry.grid(row=0, column=1)

    Label(root, text="Risk Appetite (low/medium/high)").grid(row=1, column=0)
    risk_entry = Entry(root)
    risk_entry.grid(row=1, column=1)

    Label(root, text="Initial Investment").grid(row=2, column=0)
    invest_entry = Entry(root)
    invest_entry.grid(row=2, column=1)

    output = Text(root, width=60, height=15)
    output.grid(row=4, column=0, columnspan=2)

    def on_analyze():
        symbol = symbol_entry.get().strip().upper()
        risk = risk_entry.get().strip().lower()
        try:
            investment = float(invest_entry.get())
        except ValueError:
            investment = 0.0
        result = analyze_stock(symbol, risk, investment)
        output.delete("1.0", END)
        output.insert(END, f"Decision: {result['decision']}\n")
        if result["when"]:
            output.insert(END, result["when"] + "\n")
        if result["portfolio"]:
            output.insert(END, "Suggested Portfolio:\n")
            for s, amt in result["portfolio"].items():
                output.insert(END, f"  {s}: ₹{amt:.2f}\n")

    Button(root, text="Analyze", command=on_analyze).grid(row=3, column=0, columnspan=2)
    return root


if __name__ == "__main__":
    app = build_gui()
    app.mainloop()
