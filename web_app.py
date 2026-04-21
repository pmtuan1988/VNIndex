from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI, Header, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from scripts.mcp_vnstock_server import get_stock_trading_30d

app = FastAPI(title="VNIndex Web App", version="0.1.0")

WEB_DIR = Path(__file__).parent / "web"
app.mount("/assets", StaticFiles(directory=WEB_DIR), name="assets")


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/api/stock/{symbol}")
def stock(
    symbol: str,
    days: int = Query(30, ge=1, le=180),
    authorization: str | None = Header(default=None),
) -> dict:
    # Try FireAnt first if Bearer token provided in header or env var
    fa_token = ""
    if authorization and authorization.lower().startswith("bearer "):
        fa_token = authorization[7:].strip()
    if not fa_token:
        fa_token = os.environ.get("FIREANT_TOKEN", "").strip()

    if fa_token:
        try:
            from scripts.fireant_client import fetch_shb_30d
            return fetch_shb_30d(token=fa_token, symbol=symbol.upper(), days=days)
        except Exception:  # noqa: BLE001
            pass  # fall through to vnstock

    try:
        return get_stock_trading_30d(
            symbol=symbol.upper(),
            days=days,
            preferred_sources="TCBS,DNSE,KBS,VCI",
        )
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/")
def index() -> FileResponse:
    return FileResponse(WEB_DIR / "index.html")
