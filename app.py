from pathlib import Path

from fastapi import FastAPI, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from gold_daily_analysis import add_indicators, download_data, make_analysis

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"

app = FastAPI(title="Gold Daily Analysis")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/")
def index():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/api/gold")
def gold(
    ticker: str = Query("GC=F", min_length=1),
    period: str = Query("1y", pattern="^(6mo|1y|2y|5y|10y)$"),
):
    df = add_indicators(download_data(ticker, period))
    analysis = make_analysis(df, ticker)
    history = []
    for index, row in df.tail(260).iterrows():
        history.append({
            "date": str(index.date()),
            "close": round(float(row["Close"]), 2),
            "sma20": round(float(row["SMA20"]), 2) if row["SMA20"] == row["SMA20"] else None,
            "sma50": round(float(row["SMA50"]), 2) if row["SMA50"] == row["SMA50"] else None,
            "sma200": round(float(row["SMA200"]), 2) if row["SMA200"] == row["SMA200"] else None,
        })
    analysis["history"] = history
    return analysis


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
