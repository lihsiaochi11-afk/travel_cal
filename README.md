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


## 油價自動更新
- GitHub Actions 每週日 16:30 UTC（台灣週一 00:30）自動執行
- 從中油官網抓取最新油價，更新 `oil_prices.json`
- 可手動觸發：Actions → 每週自動更新油價 → Run workflow


