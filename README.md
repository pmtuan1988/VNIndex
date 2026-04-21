# VNIndex

Website hiển thị thông tin giao dịch cổ phiếu **SHB** trong 1 tháng gần nhất từ 2 nguồn **TCBS** và **DNSE** thông qua thư viện `vnstock`.

## Chạy project

```bash
python -m pip install -r requirements.txt
python app.py
```

Mở trình duyệt tại:

- `http://localhost:8000` để xem website
- `http://localhost:8000/api/shb/last-month` để xem JSON API
