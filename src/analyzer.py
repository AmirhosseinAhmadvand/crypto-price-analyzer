"""
Module for analyzing cryptocurrency price trends.
Uses Moving Average to identify market trends.
"""

import pandas as pd
import numpy as np
from typing import Optional


class CryptoAnalyzer:
    """Analyzes cryptocurrency price data and generates trading signals."""
    
    def __init__(self, short_window: int = 7, long_window: int = 30):
        """
        Initialize analyzer with moving average windows.
        
        Args:
            short_window: Short-term moving average period (days)
            long_window: Long-term moving average period (days)
        """
        self.short_window = short_window
        self.long_window = long_window
    
    def calculate_moving_averages(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculates short and long-term moving averages.
        
        Args:
            df: DataFrame with 'date' and 'price' columns
            
        Returns:
            DataFrame with added MA columns
        """
        if df.empty:
            return df
        
        df = df.copy()
        df['MA_short'] = df['price'].rolling(window=self.short_window).mean()
        df['MA_long'] = df['price'].rolling(window=self.long_window).mean()
        
        return df
    
    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Generates trading signals based on moving average crossover.
        
        Signal Logic:
        - BUY: When short MA crosses above long MA
        - SELL: When short MA crosses below long MA
        - HOLD: No clear signal
        
        Args:
            df: DataFrame with MA columns
            
        Returns:
            DataFrame with added 'signal' column
        """
        if df.empty or 'MA_short' not in df.columns:
            return df
        
        df = df.copy()
        df['signal'] = 'HOLD'
        
        # Calculate signal
        df.loc[df['MA_short'] > df['MA_long'], 'signal'] = 'BUY'
        df.loc[df['MA_short'] < df['MA_long'], 'signal'] = 'SELL'
        
        # Remove signals where MA is NaN (insufficient data)
        df.loc[df['MA_short'].isna() | df['MA_long'].isna(), 'signal'] = 'HOLD'
        
        return df
    
    def get_latest_signal(self, df: pd.DataFrame) -> dict:
        """
        Gets the most recent trading signal and price info.
        
        Args:
            df: DataFrame with signal column
            
        Returns:
            Dictionary with latest signal info
        """
        if df.empty:
            return {
                'signal': 'NO_DATA',
                'price': None,
                'date': None,
                'trend': 'UNKNOWN'
            }
        
        latest = df.iloc[-1]
        
        # Determine trend
        if len(df) >= 2:
            price_change = df['price'].iloc[-1] - df['price'].iloc[-2]
            trend = 'UP' if price_change > 0 else 'DOWN'
        else:
            trend = 'UNKNOWN'
        
        return {
            'signal': latest['signal'],
            'price': latest['price'],
            'date': latest['date'],
            'trend': trend,
            'ma_short': latest.get('MA_short'),
            'ma_long': latest.get('MA_long')
        }
    
    def analyze(self, df: pd.DataFrame) -> tuple:
        """
        Complete analysis pipeline.
        
        Args:
            df: Raw price DataFrame
            
        Returns:
            Tuple of (analyzed DataFrame, latest signal dict)
        """
        if df.empty:
            return df, {'signal': 'NO_DATA'}
        
        # Calculate moving averages
        df = self.calculate_moving_averages(df)
        
        # Generate signals
        df = self.generate_signals(df)
        
        # Get latest signal
        latest_signal = self.get_latest_signal(df)
        
        return df, latest_signal


# Quick test
if __name__ == "__main__":
    # Create sample data for testing
    dates = pd.date_range(start='2026-01-01', periods=40, freq='D')
    prices = np.random.uniform(40000, 50000, 40)
    
    sample_df = pd.DataFrame({
        'date': dates,
        'price': prices
    })
    
    analyzer = CryptoAnalyzer(short_window=7, long_window=14)
    analyzed_df, signal = analyzer.analyze(sample_df)
    
    print("Latest Signal:")
    print(signal)
    print("\nLast 5 records:")
    print(analyzed_df.tail())
