from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from scripts.mcp_vnstock_server import get_stock_trading_30d


def main() -> None:
    output = Path("docs/data/shb_30d_latest.json")
    output.parent.mkdir(parents=True, exist_ok=True)

    try:
        payload = get_stock_trading_30d(
            symbol="SHB",
            days=30,
            preferred_sources="TCBS,DNSE,KBS,VCI",
        )
        payload["updated_at"] = datetime.now(timezone.utc).isoformat()
        payload.pop("last_error", None)
    except Exception as exc:  # noqa: BLE001
        if output.exists():
            payload = json.loads(output.read_text(encoding="utf-8"))
            payload["updated_at"] = datetime.now(timezone.utc).isoformat()
            payload["last_error"] = str(exc)
            payload["stale"] = True
            print("WARN: provider failed, keep last successful data")
        else:
            raise

    payload.setdefault("stale", False)

    with output.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print(f"Updated {output} rows={payload.get('rows')} source={payload.get('source_used')}")


if __name__ == "__main__":
    main()
