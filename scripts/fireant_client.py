from __future__ import annotations

"""
FireAnt REST API client — /symbols/{symbol}/historical-quotes
Docs: https://api.fireant.vn (Swagger v1.json)

Auth: Bearer token via Authorization header.
Get your token from: https://accounts.fireant.vn/connect/authorize
Or set env var FIREANT_TOKEN before running.
"""

import os
from datetime import date, timedelta
from typing import List, Dict, Optional
import urllib.request
import urllib.parse
import json

BASE_URL = "https://api.fireant.vn"


class FireAntClient:
    def __init__(self, token: Optional[str] = None) -> None:
        self.token = token or os.environ.get("FIREANT_TOKEN", "")
        if not self.token:
            raise ValueError(
                "FireAnt token is required. "
                "Set FIREANT_TOKEN env var or pass token= argument."
            )

    def _headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/json",
            "User-Agent": "vnindex-app/1.0",
        }

    def historical_quotes(
        self,
        symbol: str,
        start_date: date,
        end_date: date,
        offset: int = 0,
        limit: int = 100,
    ) -> List[Dict]:
        """
        GET /symbols/{symbol}/historical-quotes
        Returns list of OHLCV records sorted ascending by date.
        """
        params = urllib.parse.urlencode({
            "startDate": start_date.isoformat(),
            "endDate": end_date.isoformat(),
            "offset": offset,
            "limit": limit,
        })
        url = f"{BASE_URL}/symbols/{symbol.upper()}/historical-quotes?{params}"
        req = urllib.request.Request(url, headers=self._headers())
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read().decode())
        return data  # list of HistoricalQuote objects

    def historical_quotes_paged(
        self,
        symbol: str,
        start_date: date,
        end_date: date,
        page_size: int = 100,
    ) -> List[Dict]:
        """Fetch all pages and return combined list sorted by date ascending."""
        all_rows: List[Dict] = []
        offset = 0
        while True:
            batch = self.historical_quotes(
                symbol=symbol,
                start_date=start_date,
                end_date=end_date,
                offset=offset,
                limit=page_size,
            )
            if not batch:
                break
            all_rows.extend(batch)
            if len(batch) < page_size:
                break
            offset += page_size
        all_rows.sort(key=lambda r: r.get("date", ""))
        return all_rows


def normalize_row(row: Dict) -> Dict:
    """Map FireAnt field names to standard OHLCV names used by this app."""
    return {
        "time": row.get("date", ""),
        "open": row.get("priceOpen"),
        "high": row.get("priceHigh"),
        "low": row.get("priceLow"),
        "close": row.get("priceClose"),
        "volume": row.get("totalVolume"),
        # extras kept for richer display
        "price_avg": row.get("priceAverage"),
        "price_ref": row.get("priceBasic"),
        "deal_volume": row.get("dealVolume"),
        "total_value": row.get("totalValue"),
        "buy_foreign": row.get("buyForeignQuantity"),
        "sell_foreign": row.get("sellForeignQuantity"),
    }


def fetch_shb_30d(token: str, symbol: str = "SHB", days: int = 30) -> Dict:
    client = FireAntClient(token=token)
    end_date = date.today()
    start_date = end_date - timedelta(days=max(days * 3, 60))

    raw = client.historical_quotes_paged(
        symbol=symbol,
        start_date=start_date,
        end_date=end_date,
    )
    rows = [normalize_row(r) for r in raw[-days:]]

    return {
        "symbol": symbol.upper(),
        "days": days,
        "source_used": "FIREANT",
        "rows": len(rows),
        "data": rows,
        "source_errors": {},
    }
