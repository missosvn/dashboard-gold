# Gold Analysis Dashboard

Dashboard phân tích kỹ thuật giá vàng hàng ngày.

## Cấu trúc

- `gold_daily_analysis.py`: engine phân tích kỹ thuật.
- `app.py`: FastAPI backend.
- `static/index.html`: UI dashboard và biểu đồ.
- `requirements.txt`: dependencies.

## Chạy local

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Mở:

http://127.0.0.1:8000

Dashboard mặc định dùng `GC=F` (Gold Futures) từ Yahoo Finance.

> Đây là dashboard phân tích kỹ thuật tự động, không phải khuyến nghị đầu tư.
