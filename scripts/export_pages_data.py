from __future__ import annotations

import json
import os
from datetime import date, timedelta, datetime, timezone
from pathlib import Path

# Self-contained fetch — no dependency on the MCP server module
SOURCES = ["TCBS", "DNSE", "KBS", "VCI"]


def _fetch_shb_fireant(symbol: str = "SHB", days: int = 30):
    """Fetch from FireAnt API if FIREANT_TOKEN env var is set."""
    token = os.environ.get("FIREANT_TOKEN", "").strip()
    if not token:
        raise ValueError("FIREANT_TOKEN not set")
    # Import here so vnstock import errors don't block FireAnt path
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from scripts.fireant_client import fetch_shb_30d
    return fetch_shb_30d(token=token, symbol=symbol, days=days)


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
        # FireAnt preferred — exact historical data
        payload = _fetch_shb_fireant(symbol="SHB", days=30)
        print(f"FireAnt OK: rows={payload.get('rows')}")
    except Exception as fa_exc:
        print(f"FireAnt unavailable ({fa_exc}), falling back to vnstock...")
        try:
            payload = _fetch_shb(symbol="SHB", days=30)
        except Exception as exc:
            if output.exists():
                payload = json.loads(output.read_text(encoding="utf-8"))
                payload["updated_at"] = datetime.now(timezone.utc).isoformat()
                payload["last_error"] = str(exc)
                payload["stale"] = True
                print("WARN: all sources failed, keeping last data")
                with output.open("w", encoding="utf-8") as f:
                    json.dump(payload, f, ensure_ascii=False, indent=2)
                print(f"Kept stale data rows={payload.get('rows')}")
                return
            else:
                raise

    payload["updated_at"] = datetime.now(timezone.utc).isoformat()
    payload["stale"] = False
    payload.pop("last_error", None)

    with output.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print(f"Updated {output} rows={payload.get('rows')} source={payload.get('source_used')} stale=False")


if __name__ == "__main__":
    main()
