from __future__ import annotations

import csv
import json
from pathlib import Path
from datetime import datetime
import pandas as pd

from mcp_vnstock_server import get_stock_trading_30d


class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime, pd.Timestamp)):
            return obj.isoformat()
        return super().default(obj)


def main() -> None:
    result = get_stock_trading_30d(symbol="SHB", days=30, preferred_sources="TCBS,DNSE,KBS,VCI")

    data_dir = Path("data")
    data_dir.mkdir(parents=True, exist_ok=True)

    json_path = data_dir / "shb_30d_latest.json"
    csv_path = data_dir / "shb_30d_latest.csv"

    with json_path.open("w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2, cls=DateTimeEncoder)

    rows = result["data"]
    headers = list(rows[0].keys()) if rows else []
    with csv_path.open("w", encoding="utf-8", newline="") as f:
        if headers:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            writer.writerows(rows)

    print(f"Symbol: {result['symbol']}")
    print(f"Source used: {result['source_used']}")
    print(f"Rows: {result['rows']}")
    print(f"JSON: {json_path}")
    print(f"CSV: {csv_path}")


if __name__ == "__main__":
    main()
