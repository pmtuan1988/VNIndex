from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from scripts.mcp_vnstock_server import get_stock_trading_30d


def main() -> None:
    payload = get_stock_trading_30d(
        symbol="SHB",
        days=30,
        preferred_sources="TCBS,DNSE,KBS,VCI",
    )
    payload["updated_at"] = datetime.now(timezone.utc).isoformat()

    output = Path("docs/data/shb_30d_latest.json")
    output.parent.mkdir(parents=True, exist_ok=True)

    with output.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print(f"Updated {output} rows={payload.get('rows')} source={payload.get('source_used')}")


if __name__ == "__main__":
    main()
