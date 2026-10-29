"""
Module for fetching cryptocurrency data from CoinGecko API.
Includes caching and fallback mechanisms for reliability.
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
    
    def _get_cache_path(self, symbol: str) -> Path:
        """Returns the cache file path for a given symbol."""
        return self.cache_dir / f"{symbol}_cache.json"
    
    def _is_cache_valid(self, cache_path: Path) -> bool:
        """Checks if cache file exists and is not expired."""
        if not cache_path.exists():
            return False
        cache_time = datetime.fromtimestamp(cache_path.stat().st_mtime)
        return (datetime.now() - cache_time) < timedelta(hours=self.cache_hours)
    
    def _load_from_cache(self, cache_path: Path) -> pd.DataFrame:
        """Loads data from cache file."""
        with open(cache_path, 'r') as f:
            data = json.load(f)
        return pd.DataFrame(data)
    
    def _save_to_cache(self, df: pd.DataFrame, cache_path: Path):
        """Saves data to cache file."""
        with open(cache_path, 'w') as f:
            json.dump(df.to_dict(orient='records'), f)
    
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
        
        # Try cache first
        if self._is_cache_valid(cache_path):
            print(f"[INFO] Using cached data for {symbol}")
            return self._load_from_cache(cache_path)
        
        # Try API
        try:
            print(f"[INFO] Fetching data from API for {symbol}...")
            url = f"{self.api_url}/coins/{symbol}/market_chart"
            params = {"vs_currency": "usd", "days": days}
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            prices = data.get('prices', [])
            
            if not prices:
                raise ValueError(f"No price data returned for {symbol}")
            
            df = pd.DataFrame(prices, columns=['timestamp', 'price'])
            df['date'] = pd.to_datetime(df['timestamp'], unit='ms')
            df = df[['date', 'price']]
            
            # Save to cache
            self._save_to_cache(df, cache_path)
            print(f"[SUCCESS] Fetched and cached {len(df)} records")
            return df
            
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] API request failed: {e}")
            
            # Fallback to expired cache if exists
            if cache_path.exists():
                print("[WARNING] Using expired cache as fallback")
                return self._load_from_cache(cache_path)
            
            # Final fallback: return empty DataFrame
            print("[WARNING] No data available, returning empty DataFrame")
            return pd.DataFrame(columns=['date', 'price'])


# Quick test
if __name__ == "__main__":
    scraper = CryptoScraper()
    df = scraper.fetch_prices("bitcoin", days=7)
    print("\nLast 5 records:")
    print(df.tail())
