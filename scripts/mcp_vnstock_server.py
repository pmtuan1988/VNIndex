from __future__ import annotations

from datetime import date, timedelta
from typing import Dict, List, Tuple

from mcp.server.fastmcp import FastMCP
from vnstock import Vnstock

mcp = FastMCP("vnstock-mcp")
DEFAULT_SOURCES = ["TCBS", "DNSE", "KBS", "VCI"]


def _to_json_value(value):
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return value


def _normalize_sources(preferred_sources: str) -> List[str]:
    parsed = [s.strip().upper() for s in preferred_sources.split(",") if s.strip()]
    if not parsed:
        return DEFAULT_SOURCES.copy()

    ordered = []
    seen = set()
    for source in parsed + DEFAULT_SOURCES:
        if source not in seen:
            ordered.append(source)
            seen.add(source)
    return ordered


def _fetch_history_with_fallback(
    symbol: str, days: int, preferred_sources: str
) -> Tuple[str, List[Dict], Dict[str, str]]:
    sources = _normalize_sources(preferred_sources)
    errors: Dict[str, str] = {}

    end_date = date.today()
    start_date = end_date - timedelta(days=max(days * 3, 45))

    for source in sources:
        try:
            stock = Vnstock().stock(symbol=symbol.upper(), source=source)
            df = stock.quote.history(
                start=start_date.isoformat(),
                end=end_date.isoformat(),
                interval="1D",
            )
            if df is None or df.empty:
                raise ValueError("No data returned")

            df = df.sort_values("time").tail(days).reset_index(drop=True)
            rows = []
            for row in df.to_dict(orient="records"):
                rows.append({k: _to_json_value(v) for k, v in row.items()})
            return source, rows, errors
        except Exception as exc:  # noqa: BLE001
            errors[source] = str(exc)

    raise RuntimeError(
        "Unable to fetch data from all sources. "
        f"Tried {sources}. Errors: {errors}"
    )


@mcp.tool()
def get_stock_trading_30d(
    symbol: str = "SHB",
    days: int = 30,
    preferred_sources: str = "TCBS,DNSE,KBS,VCI",
) -> Dict:
    """
    Fetch latest trading history for a symbol with source fallback.

    Args:
      symbol: Ticker symbol, e.g. SHB.
      days: Number of latest sessions to return.
      preferred_sources: CSV source priority. Example: "TCBS,DNSE,KBS,VCI".
    """
    if days < 1:
        raise ValueError("days must be >= 1")

    used_source, rows, errors = _fetch_history_with_fallback(symbol, days, preferred_sources)

    return {
        "symbol": symbol.upper(),
        "days": days,
        "source_used": used_source,
        "rows": len(rows),
        "data": rows,
        "source_errors": errors,
    }


if __name__ == "__main__":
    mcp.run()
