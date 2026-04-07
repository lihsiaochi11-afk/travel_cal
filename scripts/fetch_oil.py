#!/usr/bin/env python3
"""
每週自動抓取中油95無鉛汽油歷史油價
來源：中油官方 XML Web Service
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

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'zh-TW,zh;q=0.9',
}

def fetch_current_price():
    """從中油官方 XML Web Service 取得當前油價"""
    urls = [
        'https://vipmbr.cpc.com.tw/CPCSTN/ListPriceWebService.asmx/getCPCMainProdListPrice_XML',
        'https://vipmember.tmtd.cpc.com.tw/opendata/ListPriceWebService.asmx/getCPCMainProdListPrice_XML',
    ]
    for url in urls:
        try:
            res = requests.get(url, headers=HEADERS, timeout=15)
            if res.status_code == 200:
                # XML 格式：92、95、98、柴油順序
                prices = re.findall(r'<參考牌價>([\d.]+)</參考牌價>', res.text)
                if not prices:
                    # 英文版 tag
                    prices = re.findall(r'<PRICE>([\d.]+)</PRICE>', res.text)
                if len(prices) >= 2:
                    price_95 = float(prices[1])
                    if 15 < price_95 < 60:
                        print(f"✓ 當前95無鉛油價：{price_95} 元（來源：中油XML API）")
                        return price_95
        except Exception as e:
            print(f"  嘗試 {url} 失敗：{e}")
    return None

def fetch_history_from_igcar():
    """從 igcar.com.tw 抓取歷史油價"""
    # igcar 提供每週油價，格式穩定
    url = 'https://igcar.com.tw/gas/'
    try:
        res = requests.get(url, headers=HEADERS, timeout=15)
        if res.status_code != 200:
            return {}

        # 找所有週期油價：格式如 "2026/03/02 - 2026/03/08"
        # 和對應的95油價
        prices = {}
        # 找日期範圍和95無鉛油價
        blocks = re.findall(
            r'(\d{4}/\d{2}/\d{2})\s*-\s*\d{4}/\d{2}/\d{2}.*?95[^<]*?<[^>]+>\s*([\d.]+)\s*元',
            res.text, re.DOTALL
        )
        for date_str, price_str in blocks:
            try:
                # 轉換日期格式
                d = datetime.strptime(date_str, '%Y/%m/%d')
                date_key = d.strftime('%Y-%m-%d')
                price = float(price_str)
                if 15 < price < 60:
                    prices[date_key] = price
            except:
                pass

        if prices:
            print(f"✓ 從 igcar 取得 {len(prices)} 週歷史油價")
        return prices
    except Exception as e:
        print(f"igcar 失敗：{e}")
        return {}

def get_this_monday():
    """取得本週一的日期"""
    today = datetime.now()
    days_since_monday = today.weekday()
    monday = today - timedelta(days=days_since_monday)
    return monday.strftime('%Y-%m-%d')

def main():
    output_path = Path(__file__).parent.parent / 'oil_prices.json'

    # 讀取現有資料
    existing = {}
    if output_path.exists():
        with open(output_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            existing = data.get('prices', {})
        print(f"現有資料：{len(existing)} 週")

    # 取得當前油價
    current_price = fetch_current_price()

    # 取得歷史油價
    history = fetch_history_from_igcar()

    # 合併資料
    merged = {**existing, **history}

    # 加入本週油價（用當前 API 確保準確）
    if current_price:
        monday = get_this_monday()
        merged[monday] = current_price
        print(f"✓ 本週（{monday}）油價：{current_price} 元")

    if not merged:
        print("✗ 所有來源均失敗，保留現有資料")
        if not existing:
            sys.exit(1)
        merged = existing

    # 只保留近兩年
    cutoff = (datetime.now() - timedelta(days=730)).strftime('%Y-%m-%d')
    merged = {k: v for k, v in merged.items() if k >= cutoff}

    output = {
        "updated_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "source": "台灣中油 95無鉛汽油每週參考零售價",
        "unit": "元/公升",
        "prices": dict(sorted(merged.items()))
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    sorted_dates = sorted(merged.keys())
    print(f"\n✓ 已寫出 {output_path}")
    print(f"  共 {len(merged)} 週，最新：{sorted_dates[-1]} = {merged[sorted_dates[-1]]} 元")

if __name__ == '__main__':
    main()
