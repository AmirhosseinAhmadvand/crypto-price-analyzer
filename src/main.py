"""
Main entry point for the Crypto Price Analyzer.
Shows real-time price and trend analysis.
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
    
    symbol = "bitcoin"
    days = 30
    
    # Step 1: Get current price
    print(f"\n[1/4] Fetching current price for {symbol}...")
    scraper = CryptoScraper(cache_dir="data", cache_hours=1)
    current_data = scraper.get_current_price(symbol)
    
    if current_data.get("price") is None:
        print("\n[ERROR] Cannot fetch current price. Exiting.")
        sys.exit(1)
    
    print(f"[SUCCESS] Current Price: ${current_data['price']:,.2f} {current_data['currency']}")
    print(f"[INFO] Updated at: {current_data['timestamp']}")
    if current_data.get("note"):
        print(f"[WARNING] {current_data['note']}")
    
    # Step 2: Fetch historical data
    print(f"\n[2/4] Fetching historical data (last {days} days)...")
    df = scraper.fetch_prices(symbol, days)
    
    if df.empty:
        print("\n[ERROR] No historical data available. Exiting.")
        sys.exit(1)
    
    print(f"[SUCCESS] Fetched {len(df)} records")
    
    # Step 3: Analyze trends
    print(f"\n[3/4] Analyzing trends...")
    analyzer = CryptoAnalyzer(short_window=7, long_window=14)
    analyzed_df, signal = analyzer.analyze(df)
    
    # Step 4: Display results
    print(f"\n[4/4] Analysis Results:")
    print("-" * 60)
    print(f"Symbol: {symbol.upper()}")
    print(f"Current Price: ${current_data['price']:,.2f}")
    print(f"Trend (30-day): {signal['trend']}")
    print(f"Signal: {signal['signal']}")
    print("-" * 60)
    
    if signal['signal'] == 'BUY':
        print("\n💡 Recommendation: Consider buying")
    elif signal['signal'] == 'SELL':
        print("\n💡 Recommendation: Consider selling")
    else:
        print("\n💡 Recommendation: Hold position")
    
    # Save results
    output_path = Path("data") / f"{symbol}_analysis.csv"
    analyzed_df.to_csv(output_path, index=False)
    print(f"\n[INFO] Results saved to {output_path}")
    
    print("\n" + "=" * 60)
    print("Analysis complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
