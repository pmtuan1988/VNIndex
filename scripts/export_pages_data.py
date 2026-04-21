from __future__ import annotations

import json
from datetime import date, timedelta, datetime, timezone
from pathlib import Path

# Self-contained fetch — no dependency on the MCP server module
SOURCES = ["TCBS", "DNSE", "KBS", "VCI"]


def _fetch_shb(symbol: str = "SHB", days: int = 30):
    from vnstock import Vnstock

    end_date = date.today()
    start_date = end_date - timedelta(days=max(days * 3, 45))
    errors = {}

    for source in SOURCES:
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
                rows.append({k: (v.isoformat() if hasattr(v, "isoformat") else v) for k, v in row.items()})
            return {
                "symbol": symbol.upper(),
                "days": days,
                "source_used": source,
                "rows": len(rows),
                "data": rows,
                "source_errors": errors,
            }
        except Exception as exc:  # noqa: BLE001
            errors[source] = str(exc)
 

    raise RuntimeError(f"All sources failed: {errors}")


def main() -> None:
    output = Path("docs/data/shb_30d_latest.json")
    output.parent.mkdir(parents=True, exist_ok=True)

    try:
        payload = _fetch_shb(symbol="SHB", days=30)
    except Exception as exc:
        print(f"WARN: fetch failed ({exc}), keeping last data")
        if output.exists():
            payload = json.loads(output.read_text(encoding="utf-8"))
            payload["updated_at"] = datetime.now(timezone.utc).isoformat()
            payload["last_error"] = str(exc)
            payload["stale"] = True
            with output.open("w", encoding="utf-8") as f:
                json.dump(payload, f, ensure_ascii=False, indent=2)
            print(f"Kept stale data rows={payload.get('rows')}")
            return
        raise

    payload["updated_at"] = datetime.now(timezone.utc).isoformat()
    payload["stale"] = False
    payload.pop("last_error", None)

    with output.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print(f"Updated {output} rows={payload.get('rows')} source={payload.get('source_used')} stale={payload.get('stale')}")


if __name__ == "__main__":
    main()
