# VNIndex

MCP integration for Vietnam stock data using `vnstock`.

## What this repo now includes

- An MCP server: `scripts/mcp_vnstock_server.py`
- A one-shot fetch script: `scripts/fetch_shb_30d.py`

## Notes about sources

You asked for `TCBS`/`DNSE`. In current `vnstock` versions, these sources are not available in the active API surface and will raise an error.

The MCP tool and fetch script still try sources in this order:

1. `TCBS`
2. `DNSE`
3. `KBS`
4. `VCI`

So if `TCBS`/`DNSE` is unavailable, it automatically falls back to a working source and returns data.

## Setup

```powershell
cd d:\VNIndex
uv sync
```

## Fetch SHB 30 sessions now

```powershell
cd d:\VNIndex
uv run python scripts/fetch_shb_30d.py
```

Output files:

- `data/shb_30d_latest.csv`
- `data/shb_30d_latest.json`

## Run MCP server (stdio)

```powershell
cd d:\VNIndex
uv run python scripts/mcp_vnstock_server.py
```

Exposed MCP tool:

- `get_stock_trading_30d(symbol="SHB", days=30, preferred_sources="TCBS,DNSE,KBS,VCI")`

## Web app xem online

### Chạy local

```powershell
cd d:\VNIndex
uv sync
uv run uvicorn web_app:app --host 0.0.0.0 --port 8000 --reload
```

Mở trình duyệt:

- `http://localhost:8000`

API:

- `GET /api/stock/SHB?days=30`
- `GET /health`

UI hiện có auto refresh:

- Tùy chọn `5 giây` hoặc `10 giây`
- Có thể tắt bằng `Tắt auto refresh`

### Kết nối với repo GitHub

Repo đang dùng:

- `https://github.com/pmtuan1988/VNIndex`

Bạn có thể đẩy code web app này lên cùng repo để triển khai online trên các nền tảng như Render, Railway, hoặc Azure App Service.

## Chay online tren GitHub Pages

Ban muon chay tren GitHub thi dung luong nay (khong qua Render):

1. Push code len repo `https://github.com/pmtuan1988/VNIndex`
2. Vao `Settings` -> `Pages`
3. Tai `Build and deployment`, chon `Source = GitHub Actions`
4. Chay workflow `Update Pages Data` (run tay 1 lan dau)
5. Workflow `Deploy GitHub Pages` se publish web trong `docs/`

URL du kien:

- `https://pmtuan1988.github.io/VNIndex/`

Da co san trong repo:

- Frontend GitHub Pages: `docs/index.html`
- Du lieu cho Pages: `docs/data/shb_30d_latest.json`
- Workflow cap nhat du lieu 10 phut/lần: `.github/workflows/update-pages-data.yml`
- Workflow deploy Pages: `.github/workflows/deploy-pages.yml`

Luu y ky thuat:

- GitHub Pages la static hosting, khong chay backend FastAPI.
- Auto refresh 5-10 giay tren giao dien da co, nhung file du lieu duoc cap nhat theo lich GitHub Actions (10 phut/lần).

### Deploy bằng Docker

Build image:

```powershell
cd d:\VNIndex
docker build -t vnindex-web:latest .
```

Run local bằng Docker:

```powershell
docker run --rm -p 8000:8000 vnindex-web:latest
```

Khi deploy cloud, command chạy app:

- `uv run uvicorn web_app:app --host 0.0.0.0 --port 8000`
