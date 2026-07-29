# Copyright (c) 2026 Samuel Gobbi (Ezpeon). Licensed under the MIT License (see LICENSE).

from pathlib import Path

import yfinance as yf

BASE_DIR = Path(__file__).resolve().parent

NAMES = {
    "sp500_monthly.csv": "^GSPC",
    "btc_monthly.csv": "BTC-USD",
    "au_monthly.csv": "GC=F",
    "eth_monthly.csv": "ETH-USD",
}

for filename, ticker in NAMES.items():
    close = yf.download(ticker, start="2021-06-01", interval="1mo")["Close"]
    close.to_csv(BASE_DIR / filename)
