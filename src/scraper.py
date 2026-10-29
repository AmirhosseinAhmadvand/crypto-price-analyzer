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
        """
        Fetches historical price data for a cryptocurrency.
        
        Args:
            symbol: Coin ID (e.g., 'bitcoin', 'ethereum')
            days: Number of days of historical data
            
        Returns:
            DataFrame with 'date' and 'price' columns
        """
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
    
    def get_current_price(self, symbol: str = "bitcoin") -> dict:
        """
        Fetches the current real-time price of a cryptocurrency.
        
        Returns:
            Dictionary with 'price', 'currency', and 'timestamp'
        """
        cache_path = self.cache_dir / f"{symbol}_current.json"
        
        # Try cache first (cache for 5 minutes)
        if self._is_cache_valid(cache_path):
            print(f"[INFO] Using cached current price for {symbol}")
            with open(cache_path, 'r') as f:
                return json.load(f)
        
        # Try API
        try:
            print(f"[INFO] Fetching current price for {symbol}...")
            url = f"{self.api_url}/simple/price"
            params = {
                "ids": symbol,
                "vs_currencies": "usd",
                "include_last_updated_at": "true"
            }
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if symbol not in data:
                raise ValueError(f"No data for {symbol}")
            
            result = {
                "price": data[symbol]["usd"],
                "currency": "USD",
                "timestamp": datetime.fromtimestamp(data[symbol]["last_updated_at"]).isoformat()
            }
            
            # Save to cache
            with open(cache_path, 'w') as f:
                json.dump(result, f)
            
            print(f"[SUCCESS] Current price: ${result['price']:,.2f}")
            return result
            
        except Exception as e:
            print(f"[ERROR] Failed to fetch current price: {e}")
            
            # Fallback to sample data
            if self.sample_data_path.exists():
                print("[WARNING] Using sample data for current price")
                with open(self.sample_data_path, 'r') as f:
                    sample_data = json.load(f)
                last_record = sample_data[-1]
                return {
                    "price": last_record["price"],
                    "currency": "USD",
                    "timestamp": last_record["date"],
                    "note": "SAMPLE DATA (API unavailable)"
                }
            
            return {"price": None, "currency": "USD", "timestamp": None, "error": str(e)}


# Quick test
if __name__ == "__main__":
    scraper = CryptoScraper()
    
    # Test historical data
    print("=" * 60)
    print("Testing Historical Data Fetch")
    print("=" * 60)
    df = scraper.fetch_prices("bitcoin", days=7)
    print("\nLast 5 records:")
    print(df.tail())
    
    # Test current price
    print("\n" + "=" * 60)
    print("Testing Current Price Fetch")
    print("=" * 60)
    current = scraper.get_current_price("bitcoin")
    print(f"\nCurrent Price Info: {current}")
    
