from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from scripts.mcp_vnstock_server import get_stock_trading_30d

app = FastAPI(title="VNIndex Web App", version="0.1.0")

VN30_SYMBOLS = [
    "ACB", "BCM", "BID", "BVH", "CTG", "FPT", "GAS", "GVR", "HDB", "HPG",
    "MBB", "MSN", "MWG", "PLX", "POW", "SAB", "SHB", "SSB", "SSI", "STB",
    "TCB", "TPB", "VCB", "VHM", "VIB", "VIC", "VJC", "VNM", "VPB", "VRE",
]

WEB_DIR = Path(__file__).parent / "web"
app.mount("/assets", StaticFiles(directory=WEB_DIR), name="assets")


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/api/vn30")
def vn30() -> dict:
    return {"items": VN30_SYMBOLS, "rows": len(VN30_SYMBOLS)}


@app.get("/api/stock/{symbol}")
def stock(
    symbol: str,
    days: int = Query(30, ge=1, le=180),
) -> dict:
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
