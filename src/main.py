"""
Main entry point for the Crypto Price Analyzer.
Orchestrates data fetching and analysis.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.scraper import CryptoScraper
from src.analyzer import CryptoAnalyzer


def main():
    """Run the crypto price analyzer."""
    print("=" * 60)
    print("CRYPTO PRICE ANALYZER")
    print("=" * 60)
    
    # Configuration
    symbol = "bitcoin"
    days = 30
    
    print(f"\n[1/3] Fetching data for {symbol} (last {days} days)...")
    
    # Step 1: Fetch data
    scraper = CryptoScraper(cache_dir="data", cache_hours=1)
    df = scraper.fetch_prices(symbol, days)
    
    if df.empty:
        print("\n[ERROR] No data available. Exiting.")
        sys.exit(1)
    
    print(f"[SUCCESS] Fetched {len(df)} price records")
    
    # Step 2: Analyze data
    print(f"\n[2/3] Analyzing trends...")
    analyzer = CryptoAnalyzer(short_window=7, long_window=14)
    analyzed_df, signal = analyzer.analyze(df)
    
    # Step 3: Display results
    print(f"\n[3/3] Results:")
    print("-" * 60)
    print(f"Symbol: {symbol.upper()}")
    print(f"Latest Price: ${signal['price']:,.2f}")
    print(f"Date: {signal['date']}")
    print(f"Trend: {signal['trend']}")
    print(f"Signal: {signal['signal']}")
    print("-" * 60)
    
    if signal['signal'] == 'BUY':
        print("\n💡 Recommendation: Consider buying (short-term MA above long-term MA)")
    elif signal['signal'] == 'SELL':
        print("\n💡 Recommendation: Consider selling (short-term MA below long-term MA)")
    else:
        print("\n💡 Recommendation: Hold position (no clear signal)")
    
    # Save results
    output_path = Path("data") / f"{symbol}_analysis.csv"
    analyzed_df.to_csv(output_path, index=False)
    print(f"\n[INFO] Results saved to {output_path}")
    
    print("\n" + "=" * 60)
    print("Analysis complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
