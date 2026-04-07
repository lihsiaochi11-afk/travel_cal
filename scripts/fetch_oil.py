#!/usr/bin/env python3
"""
每週自動抓取中油95無鉛汽油歷史油價
來源：https://www.cpc.com.tw/cp.aspx?n=92
輸出：oil_prices.json
"""

import json
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path

try:
    import requests
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'requests'])
    import requests

def fetch_oil_prices():
    url = 'https://www.cpc.com.tw/cp.aspx?n=92'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml',
        'Accept-Language': 'zh-TW,zh;q=0.9',
    }

    print(f"正在抓取中油油價頁面...")
    res = requests.get(url, headers=headers, timeout=30)
    res.raise_for_status()
    html = res.text
    print(f"頁面取得成功，長度 {len(html)} 字元")

    # 解析 pieSeries JS 變數
    m = re.search(r'pieSeries\s*=\s*(\[[\s\S]*?\]);', html)
    if not m:
        raise ValueError("找不到 pieSeries 變數，中油頁面結構可能已變更")

    series = json.loads(m.group(1))
    print(f"解析成功，共 {len(series)} 週資料")

    # 轉換成 {YYYY-MM-DD: price} 格式
    prices = {}
    for week in series:
        name = week.get('name', '')  # 格式：114/03/31（民國年）
        parts = name.split('/')
        if len(parts) < 3:
            continue

        # 民國年轉西元
        roc_year = int(parts[0])
        western_year = roc_year + 1911
        month = int(parts[1])
        day = int(parts[2])
        date_str = f"{western_year}-{month:02d}-{day:02d}"

        # 找 95 無鉛汽油
        item95 = next((x for x in week.get('data', []) if '95' in x.get('name', '')), None)
        if item95 and item95.get('y'):
            prices[date_str] = item95['y']

    print(f"共解析 {len(prices)} 週油價")
    if prices:
        sorted_dates = sorted(prices.keys())
        print(f"最早：{sorted_dates[0]} = {prices[sorted_dates[0]]} 元")
        print(f"最新：{sorted_dates[-1]} = {prices[sorted_dates[-1]]} 元")

    return prices

def main():
    output_path = Path(__file__).parent.parent / 'oil_prices.json'

    # 讀取現有資料（如果有）
    existing = {}
    if output_path.exists():
        with open(output_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            existing = data.get('prices', {})
        print(f"現有資料：{len(existing)} 週")

    # 抓取新資料
    new_prices = fetch_oil_prices()

    # 合併（新資料優先）
    merged = {**existing, **new_prices}

    # 只保留近兩年內的資料（避免檔案過大）
    cutoff = (datetime.now() - timedelta(days=730)).strftime('%Y-%m-%d')
    merged = {k: v for k, v in merged.items() if k >= cutoff}

    # 寫出 JSON
    output = {
        "updated_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "source": "台灣中油 95無鉛汽油每週參考零售價",
        "unit": "元/公升",
        "prices": dict(sorted(merged.items()))
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\n✓ 已寫出 {output_path}，共 {len(merged)} 週資料")

if __name__ == '__main__':
    main()
