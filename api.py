"""
FastAPI Backend for Crypto Dashboard.
Serves data to the Glassmorphism Frontend.
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
import uvicorn
import webbrowser
import threading
import time

# Import our existing logic
from src.scraper import CryptoScraper
from src.analyzer import CryptoAnalyzer

app = FastAPI(title="Crypto God Dashboard")

# Setup templates
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Serve the main dashboard HTML."""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/data/{symbol}")
async def get_crypto_data(symbol: str):
    """
    API Endpoint: Fetches real-time price, history, and analysis.
    This is what the frontend calls to get data.
    """
    try:
        scraper = CryptoScraper(cache_dir="data", cache_hours=1)
        
        # 1. Get Current Price
        current_data = scraper.get_current_price(symbol)
        
        # 2. Get Historical Data for Chart
        df = scraper.fetch_prices(symbol, days=30)
        
        # 3. Analyze
        analyzer = CryptoAnalyzer(short_window=7, long_window=14)
        analyzed_df, signal = analyzer.analyze(df)
        
        # Prepare data for JSON response
        # Convert DataFrame to list of dicts for Chart.js
        chart_data = []
        for _, row in df.iterrows():
            chart_data.append({
                "x": row['date'].strftime('%Y-%m-%d'),
                "y": row['price']
            })
            
        return {
            "status": "success",
            "symbol": symbol.upper(),
            "current_price": current_data.get("price"),
            "currency": current_data.get("currency"),
            "trend": signal.get("trend"),
            "signal": signal.get("signal"),
            "recommendation_fa": get_persian_recommendation(signal.get("signal")),
            "recommendation_en": get_english_recommendation(signal.get("signal")),
            "chart_data": chart_data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def get_persian_recommendation(signal: str) -> str:
    if signal == "BUY": return "🟢 زمان خرید است (صعودی)"
    if signal == "SELL": return "🔴 زمان فروش است (نزولی)"
    return "🟡 صبر کنید (خنثی)"

def get_english_recommendation(signal: str) -> str:
    if signal == "BUY": return "🟢 Buy Signal (Bullish)"
    if signal == "SELL": return "🔴 Sell Signal (Bearish)"
    return "🟡 Hold (Neutral)"

def open_browser():
    """Automatically open browser after server starts."""
    time.sleep(1.5) # Wait for server to start
    webbrowser.open("http://127.0.0.1:8000")

if __name__ == "__main__":
    # Start browser in a separate thread
    threading.Thread(target=open_browser).start()
    # Run the server
    uvicorn.run(app, host="127.0.0.1", port=8000)
