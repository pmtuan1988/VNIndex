from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

from flask import Flask, jsonify, send_from_directory
from vnstock import stock_historical_data

BASE_DIR = Path(__file__).resolve().parent
WEB_DIR = BASE_DIR / "web"

app = Flask(__name__, static_folder=str(WEB_DIR), static_url_path="/static")


def _to_number(value):
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _fetch_source(symbol: str, source: str, start_date: str, end_date: str) -> dict:
    frame = stock_historical_data(
        symbol=symbol,
        start_date=start_date,
        end_date=end_date,
        resolution="1D",
        source=source,
        beautify=True,
    )

    trades = []
    for _, row in frame.iterrows():
        close = _to_number(row.get("close"))
        open_price = _to_number(row.get("open"))
        high = _to_number(row.get("high"))
        low = _to_number(row.get("low"))
        volume = _to_number(row.get("volume"))
        trades.append(
            {
                "time": str(row.get("time")),
                "open": open_price,
                "high": high,
                "low": low,
                "close": close,
                "volume": volume,
            }
        )

    closes = [item["close"] for item in trades if item["close"] is not None]
    volumes = [item["volume"] for item in trades if item["volume"] is not None]

    return {
        "symbol": symbol,
        "source": source,
        "start_date": start_date,
        "end_date": end_date,
        "records": len(trades),
        "summary": {
            "avg_close": (sum(closes) / len(closes)) if closes else None,
            "max_close": max(closes) if closes else None,
            "min_close": min(closes) if closes else None,
            "total_volume": sum(volumes) if volumes else None,
        },
        "trades": trades,
    }


@app.get("/api/shb/last-month")
def shb_last_month():
    symbol = "SHB"
    end = datetime.now(timezone.utc).date()
    start = end - timedelta(days=30)

    start_date = start.strftime("%Y-%m-%d")
    end_date = end.strftime("%Y-%m-%d")

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "symbol": symbol,
        "period": {"start_date": start_date, "end_date": end_date},
        "sources": {},
    }

    for source in ("TCBS", "DNSE"):
        try:
            payload["sources"][source] = _fetch_source(symbol, source, start_date, end_date)
        except Exception as exc:  # pragma: no cover - depends on external data source
            payload["sources"][source] = {"error": str(exc), "source": source}

    return jsonify(payload)


@app.get("/")
def home():
    return send_from_directory(WEB_DIR, "index.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
