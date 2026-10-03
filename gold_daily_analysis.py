"""Gold futures daily technical analysis using Yahoo Finance."""
from __future__ import annotations

import numpy as np
import pandas as pd
import yfinance as yf


def download_data(ticker: str = "GC=F", period: str = "1y") -> pd.DataFrame:
    df = yf.download(ticker, period=period, interval="1d", auto_adjust=False,
                     progress=False, threads=False)
    if df is None or df.empty:
        raise RuntimeError(f"No market data returned for {ticker}")
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [col[0] for col in df.columns]
    required = ["Open", "High", "Low", "Close", "Volume"]
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise RuntimeError(f"Missing data columns: {missing}")
    df = df[required].copy()
    for col in required:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df.dropna(subset=["Open", "High", "Low", "Close"], inplace=True)
    if len(df) < 200:
        raise RuntimeError("Not enough daily history for the 200-day moving average.")
    return df


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    close = out["Close"]
    out["ChangePct"] = close.pct_change() * 100
    out["SMA20"] = close.rolling(20).mean()
    out["SMA50"] = close.rolling(50).mean()
    out["SMA200"] = close.rolling(200).mean()
    ema12 = close.ewm(span=12, adjust=False).mean()
    ema26 = close.ewm(span=26, adjust=False).mean()
    out["MACD"] = ema12 - ema26
    out["MACD_Signal"] = out["MACD"].ewm(span=9, adjust=False).mean()
    delta = close.diff()
    gain = delta.clip(lower=0).ewm(alpha=1 / 14, adjust=False, min_periods=14).mean()
    loss = (-delta.clip(upper=0)).ewm(alpha=1 / 14, adjust=False, min_periods=14).mean()
    rs = gain / loss.replace(0, np.nan)
    out["RSI14"] = (100 - 100 / (1 + rs)).fillna(50)
    previous = close.shift(1)
    tr = pd.concat([(out["High"] - out["Low"]),
                    (out["High"] - previous).abs(),
                    (out["Low"] - previous).abs()], axis=1).max(axis=1)
    out["ATR14"] = tr.ewm(alpha=1 / 14, adjust=False, min_periods=14).mean()
    mid = close.rolling(20).mean()
    std = close.rolling(20).std()
    out["BB_Mid"] = mid
    out["BB_Upper"] = mid + 2 * std
    out["BB_Lower"] = mid - 2 * std
    out["Support20"] = out["Low"].rolling(20).min().shift(1)
    out["Resistance20"] = out["High"].rolling(20).max().shift(1)
    return out


def classify_trend(row: pd.Series) -> str:
    bullish = sum([
        row["Close"] > row["SMA20"],
        row["Close"] > row["SMA50"],
        row["Close"] > row["SMA200"],
        row["SMA20"] > row["SMA50"],
        row["SMA50"] > row["SMA200"],
        row["MACD"] > row["MACD_Signal"],
    ])
    bearish = 6 - bullish
    if bullish >= 5:
        return "TĂNG MẠNH"
    if bullish >= 4:
        return "TĂNG"
    if bearish >= 5:
        return "GIẢM MẠNH"
    if bearish >= 4:
        return "GIẢM"
    return "ĐI NGANG"


def make_analysis(df: pd.DataFrame, ticker: str) -> dict:
    row = df.iloc[-1]
    return {
        "ticker": ticker,
        "as_of": str(df.index[-1].date()),
        "close": float(row["Close"]),
        "change_pct": float(row["ChangePct"]) if pd.notna(row["ChangePct"]) else 0.0,
        "trend": classify_trend(row),
        "rsi": float(row["RSI14"]),
        "macd": float(row["MACD"]),
        "macd_signal": float(row["MACD_Signal"]),
        "atr": float(row["ATR14"]),
        "support": float(row["Support20"]),
        "resistance": float(row["Resistance20"]),
        "ma20": float(row["SMA20"]),
        "ma50": float(row["SMA50"]),
        "ma200": float(row["SMA200"]),
    }


if __name__ == "__main__":
    data = add_indicators(download_data())
    result = make_analysis(data, "GC=F")
    for key, value in result.items():
        print(f"{key}: {value}")
