from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
import uvicorn
import webbrowser
import threading
import time

from src.scraper import CryptoScraper
from src.analyzer import CryptoAnalyzer

app = FastAPI(title="Crypto God Dashboard")

HTML_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Crypto God Dashboard</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {
            background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
            min-height: 100vh;
            font-family: 'Segoe UI', sans-serif;
            color: white;
        }
        .glass-card {
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        }
    </style>
</head>
<body class="p-8">
    <div class="max-w-6xl mx-auto">
        <header class="text-center mb-10">
            <h1 class="text-5xl font-bold mb-2 bg-clip-text text-transparent bg-gradient-to-r from-cyan-400 to-purple-500">
                Crypto God Dashboard
            </h1>
            <p class="text-gray-400">Real-time Analysis</p>
        </header>

        <div class="glass-card rounded-2xl p-6 mb-8 flex justify-center gap-4">
            <input type="text" id="coinInput" value="bitcoin" 
                   class="bg-black/30 text-white px-4 py-2 rounded-lg border border-white/20 w-64">
            <button onclick="fetchData()" 
                    class="bg-gradient-to-r from-cyan-500 to-blue-500 text-white font-bold py-2 px-6 rounded-lg">
                Analyze
            </button>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <div class="glass-card rounded-2xl p-6 text-center">
                <h3 class="text-gray-400 text-sm mb-2">Current Price</h3>
                <p id="priceDisplay" class="text-4xl font-bold text-cyan-400">Loading...</p>
            </div>
            <div class="glass-card rounded-2xl p-6 text-center">
                <h3 class="text-gray-400 text-sm mb-2">Signal (EN)</h3>
                <p id="signalEn" class="text-2xl font-bold text-white">--</p>
            </div>
            <div class="glass-card rounded-2xl p-6 text-center" dir="rtl">
                <h3 class="text-gray-400 text-sm mb-2">سیگنال (فارسی)</h3>
                <p id="signalFa" class="text-2xl font-bold text-white">--</p>
            </div>
        </div>

        <div class="glass-card rounded-2xl p-6">
            <h3 class="text-xl font-bold mb-4 text-gray-300">30-Day Price Trend</h3>
            <div class="relative h-96 w-full">
                <canvas id="priceChart"></canvas>
            </div>
        </div>
    </div>

    <script>
        let myChart = null;
        async function fetchData() {
            const coin = document.getElementById('coinInput').value || 'bitcoin';
            document.getElementById('priceDisplay').innerText = "Loading...";
            try {
                const response = await fetch(`/api/data/${coin}`);
                const data = await response.json();
                if (data.status === 'success') {
                    document.getElementById('priceDisplay').innerText = `$${data.current_price.toLocaleString()}`;
                    document.getElementById('signalEn').innerText = data.recommendation_en;
                    document.getElementById('signalFa').innerText = data.recommendation_fa;
                    if (data.signal === 'BUY') {
                        document.getElementById('signalEn').className = "text-2xl font-bold text-green-400";
                        document.getElementById('signalFa').className = "text-2xl font-bold text-green-400";
                    } else if (data.signal === 'SELL') {
                        document.getElementById('signalEn').className = "text-2xl font-bold text-red-400";
                        document.getElementById('signalFa').className = "text-2xl font-bold text-red-400";
                    } else {
                        document.getElementById('signalEn').className = "text-2xl font-bold text-yellow-400";
                        document.getElementById('signalFa').className = "text-2xl font-bold text-yellow-400";
                    }
                    updateChart(data.chart_data);
                }
            } catch (error) {
                document.getElementById('priceDisplay').innerText = "Error";
            }
        }
        function updateChart(chartData) {
            const ctx = document.getElementById('priceChart').getContext('2d');
            if (myChart) myChart.destroy();
            myChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: chartData.map(d => d.x),
                    datasets: [{
                        label: 'Price (USD)',
                        data: chartData.map(d => d.y),
                        borderColor: '#00ffff',
                        borderWidth: 2,
                        fill: true,
                        tension: 0.4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { labels: { color: 'white' } } },
                    scales: {
                        x: { ticks: { color: 'gray' } },
                        y: { ticks: { color: 'gray' } }
                    }
                }
            });
        }
        window.onload = fetchData;
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def read_root():
    return HTML_CONTENT

@app.get("/api/data/{symbol}")
async def get_crypto_data(symbol: str):
    try:
        scraper = CryptoScraper(cache_dir="data", cache_hours=1)
        current_data = scraper.get_current_price(symbol)
        df = scraper.fetch_prices(symbol, days=30)
        analyzer = CryptoAnalyzer(short_window=7, long_window=14)
        analyzed_df, signal = analyzer.analyze(df)
        
        chart_data = [{"x": row['date'].strftime('%Y-%m-%d'), "y": row['price']} for _, row in df.iterrows()]
        
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
    if signal == "SELL": return " زمان فروش است (نزولی)"
    return "🟡 صبر کنید (خنثی)"

def get_english_recommendation(signal: str) -> str:
    if signal == "BUY": return "🟢 Buy Signal (Bullish)"
    if signal == "SELL": return "🔴 Sell Signal (Bearish)"
    return "🟡 Hold (Neutral)"

def open_browser():
    time.sleep(1.5)
    webbrowser.open("http://127.0.0.1:8000")

if __name__ == "__main__":
    threading.Thread(target=open_browser).start()
    uvicorn.run(app, host="127.0.0.1", port=8000)
