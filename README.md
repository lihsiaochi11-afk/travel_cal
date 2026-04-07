# 國道交通費試算器

## 檔案結構
```
├── index.html                          # 主頁面
├── oil_prices.json                     # 95無鉛汽油歷史油價（自動更新）
├── scripts/
│   └── fetch_oil.py                    # 油價抓取腳本
└── .github/workflows/
    └── update_oil.yml                  # 每週自動更新排程
```

## 部署到 GitHub Pages
1. 建立 repository，上傳所有檔案
2. Settings → Pages → Source 選 `main` branch
3. 等待部署完成，取得網址

## 油價自動更新
- GitHub Actions 每週日 16:30 UTC（台灣週一 00:30）自動執行
- 從中油官網抓取最新油價，更新 `oil_prices.json`
- 可手動觸發：Actions → 每週自動更新油價 → Run workflow

## 在 index.html 填入 API Key
找到第 472 行：
```javascript
const GOOGLE_API_KEY = 'YOUR_API_KEY_HERE';
```
換成你的 Google Geocoding API Key。
