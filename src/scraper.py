"""
Module for fetching cryptocurrency data.
Includes caching, fallback to sample data, and error handling.
"""

import requests
import pandas as pd
import json
import os
from datetime import datetime, timedelta
from pathlib import Path


class CryptoScraper:
    """Fetches and caches cryptocurrency price data."""
    
    def __init__(self, cache_dir: str = "data", cache_hours: int = 1):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.cache_hours = cache_hours
        self.api_url = "https://api.coingecko.com/api/v3"
        # مسیر فایل نمونه که ساختیم
        self.sample_data_path = self.cache_dir / "sample_data.json"
    
    def _get_cache_path(self, symbol: str) -> Path:
        return self.cache_dir / f"{symbol}_cache.json"
    
    def _is_cache_valid(self, cache_path: Path) -> bool:
        if not cache_path.exists():
            return False
        cache_time = datetime.fromtimestamp(cache_path.stat().st_mtime)
        return (datetime.now() - cache_time) < timedelta(hours=self.cache_hours)
    
    def _load_json(self, path: Path) -> pd.DataFrame:
        with open(path, 'r') as f:
            data = json.load(f)
        df = pd.DataFrame(data)
        df['date'] = pd.to_datetime(df['date'])
        return df
    
    def _save_to_cache(self, df: pd.DataFrame, cache_path: Path):
        # تبدیل به فرمت قابل ذخیره
        records = df.copy()
        records['date'] = records['date'].astype(str)
        with open(cache_path, 'w') as f:
            json.dump(records.to_dict(orient='records'), f)
    
    def fetch_prices(self, symbol: str = "bitcoin", days: int = 30) -> pd.DataFrame:
        cache_path = self._get_cache_path(symbol)
        
        # 1. Try Cache
        if self._is_cache_valid(cache_path):
            print(f"[INFO] Using cached data for {symbol}")
            return self._load_json(cache_path)
        
        # 2. Try API
        try:
            print(f"[INFO] Fetching data from API for {symbol}...")
            url = f"{self.api_url}/coins/{symbol}/market_chart"
            params = {"vs_currency": "usd", "days": days}
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            prices = data.get('prices', [])
            
            df = pd.DataFrame(prices, columns=['timestamp', 'price'])
            df['date'] = pd.to_datetime(df['timestamp'], unit='ms')
            df = df[['date', 'price']]
            
            self._save_to_cache(df, cache_path)
            print(f"[SUCCESS] Fetched and cached {len(df)} records")
            return df
            
        except Exception as e:
            print(f"[ERROR] API request failed: {e}")
            
            # 3. Fallback to Sample Data (اگر اینترنت قطع بود)
            if self.sample_data_path.exists():
                print("[WARNING] API failed. Loading sample data for demonstration...")
                return self._load_json(self.sample_data_path)
            
            print("[CRITICAL] No data available at all.")
            return pd.DataFrame(columns=['date', 'price'])
