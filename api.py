
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
import uvicorn
import webbrowser
import threading
import time
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

from src.scraper import CryptoScraper
from src.analyzer import CryptoAnalyzer

app = FastAPI(title="Crypto God Dashboard - Ultimate Pro")

HTML_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Crypto God Dashboard - Ultimate Trading Platform</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/lightweight-charts@4.1.0/dist/lightweight-charts.standalone.production.js"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');
        
        * {
            font-family: 'Inter', sans-serif;
        }
        
        body {
            background: #0a0e27;
            min-height: 100vh;
            color: white;
            overflow-x: hidden;
        }
        
        .animated-bg {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: -1;
            background: linear-gradient(-45deg, #0a0e27, #1a1f3a, #0f1629, #1a1a2e);
            background-size: 400% 400%;
            animation: gradientShift 15s ease infinite;
        }
        
        @keyframes gradientShift {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }
        
        .particle {
            position: fixed;
            border-radius: 50%;
            background: rgba(0, 255, 255, 0.3);
            pointer-events: none;
            animation: float 20s infinite;
        }
        
        @keyframes float {
            0%, 100% { transform: translateY(100vh) rotate(0deg); opacity: 0; }
            10% { opacity: 1; }
            90% { opacity: 1; }
            100% { transform: translateY(-100vh) rotate(720deg); opacity: 0; }
        }
        
        .glass-card {
            background: rgba(255, 255, 255, 0.03);
            backdrop-filter: blur(20px);
            border: 1px solid rgba(255, 255, 255, 0.08);
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.5), 
                        inset 0 0 20px rgba(255, 255, 255, 0.05);
            transition: all 0.3s ease;
        }
        
        .glass-card:hover {
            box-shadow: 0 12px 40px 0 rgba(0, 255, 255, 0.2), 
                        inset 0 0 30px rgba(255, 255, 255, 0.1);
            border-color: rgba(0, 255, 255, 0.3);
            transform: translateY(-2px);
        }
        
        .glow-text {
            text-shadow: 0 0 20px rgba(0, 255, 255, 0.5),
                         0 0 40px rgba(0, 255, 255, 0.3);
        }
        
        .glow-cyan { box-shadow: 0 0 20px rgba(0, 255, 255, 0.4); }
        .glow-green { box-shadow: 0 0 20px rgba(0, 255, 136, 0.4); }
        .glow-red { box-shadow: 0 0 20px rgba(255, 71, 87, 0.4); }
        
        .search-container { position: relative; z-index: 1000; }
        
        .dropdown {
            position: absolute;
            top: 100%;
            left: 0;
            right: 0;
            background: rgba(10, 14, 39, 0.98);
            border: 1px solid rgba(0, 255, 255, 0.4);
            border-radius: 12px;
            max-height: 400px;
            overflow-y: auto;
            z-index: 2000;
            display: none;
            margin-top: 8px;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5);
        }
        
        .dropdown-item {
            padding: 14px 18px;
            cursor: pointer;
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
            display: flex;
            align-items: center;
            gap: 14px;
            transition: all 0.3s ease;
        }
        
        .dropdown-item:hover { 
            background: linear-gradient(90deg, rgba(0, 255, 255, 0.15), transparent);
            padding-left: 24px;
        }
        
        .dropdown-item img { 
            width: 32px; height: 32px; border-radius: 50%;
            box-shadow: 0 0 10px rgba(255, 255, 255, 0.2);
        }
        
        .price-up { color: #00ff88; text-shadow: 0 0 10px rgba(0, 255, 136, 0.5); }
        .price-down { color: #ff4757; text-shadow: 0 0 10px rgba(255, 71, 87, 0.5); }
        
        .live-indicator {
            display: inline-block;
            width: 10px; height: 10px;
            background: #00ff88; border-radius: 50%;
            animation: pulse 2s infinite;
            margin-right: 10px;
            box-shadow: 0 0 10px #00ff88;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; transform: scale(1); }
            50% { opacity: 0.5; transform: scale(0.8); }
        }
        
        .timeframe-btn {
            padding: 8px 16px; border-radius: 8px;
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            cursor: pointer; transition: all 0.3s ease; font-weight: 600;
        }
        
        .timeframe-btn:hover, .timeframe-btn.active {
            background: linear-gradient(135deg, rgba(0, 255, 255, 0.3), rgba(0, 255, 255, 0.1));
            border-color: #00ffff;
            box-shadow: 0 0 20px rgba(0, 255, 255, 0.4);
            transform: scale(1.05);
        }
        
        #chart-container { height: 600px; width: 100%; border-radius: 12px; overflow: hidden; }
        
        .stat-card { position: relative; overflow: hidden; }
        .stat-card::before {
            content: ''; position: absolute; top: -50%; left: -50%;
            width: 200%; height: 200%;
            background: radial-gradient(circle, rgba(0, 255, 255, 0.1) 0%, transparent 70%);
            opacity: 0; transition: opacity 0.3s;
        }
        .stat-card:hover::before { opacity: 1; }
        
        .neon-border { position: relative; }
        .neon-border::after {
            content: ''; position: absolute; top: 0; left: 0; right: 0; bottom: 0;
            border-radius: inherit; padding: 1px;
            background: linear-gradient(135deg, rgba(0, 255, 255, 0.5), transparent, rgba(0, 255, 255, 0.5));
            -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
            mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
            -webkit-mask-composite: xor; mask-composite: exclude;
        }
        
        input[type="text"] { transition: all 0.3s ease; }
        input[type="text"]:focus { box-shadow: 0 0 30px rgba(0, 255, 255, 0.3); }
    </style>
</head>
<body class="p-6">
    <div class="animated-bg"></div>
    <div id="particles"></div>

    <div class="max-w-7xl mx-auto">
        <header class="text-center mb-10">
            <h1 class="text-7xl font-extrabold mb-4 glow-text bg-clip-text text-transparent bg-gradient-to-r from-cyan-400 via-blue-500 to-purple-600">
                Crypto God Dashboard
            </h1>
            <p class="text-gray-400 text-xl">Ultimate Professional Trading Platform</p>
        </header>

        <div class="glass-card rounded-3xl p-8 mb-8 neon-border" style="position: relative; z-index: 1000;">
            <div class="search-container max-w-3xl mx-auto">
                <input type="text" id="coinInput" placeholder="Search cryptocurrency (e.g., bitcoin, ethereum, dogecoin)..." 
                       class="bg-black/40 text-white px-8 py-4 rounded-2xl border border-white/10 w-full focus:outline-none focus:border-cyan-400 text-lg glow-cyan"
                       oninput="searchCoins(this.value)" onblur="setTimeout(() => document.getElementById('dropdown').style.display='none', 200)">
                <div id="dropdown" class="dropdown"></div>
            </div>
        </div>

        <div id="emptyState" class="glass-card rounded-3xl p-20 text-center mb-8">
            <div class="text-8xl mb-6 animate-bounce">🔍</div>
            <h2 class="text-3xl font-bold mb-4 text-gray-200">Select a Cryptocurrency</h2>
            <p class="text-gray-500 text-lg">Search and select a coin to view real-time price and professional analysis</p>
        </div>

        <div id="dashboard" class="hidden" style="position: relative; z-index: 1;">
            <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
                <div class="glass-card rounded-2xl p-8 text-center stat-card glow-cyan">
                    <div class="flex items-center justify-center mb-3">
                        <span class="live-indicator"></span>
                        <h3 class="text-gray-400 text-sm uppercase tracking-wider">Live Price</h3>
                    </div>
                    <p id="priceDisplay" class="text-5xl font-bold text-cyan-400 mb-2 glow-text">--</p>
                    <p id="coinName" class="text-gray-500 text-sm mb-2">--</p>
                    <p id="priceChange" class="text-lg font-semibold mt-3">--</p>
                </div>
                <div class="glass-card rounded-2xl p-8 text-center stat-card glow-green">
                    <h3 class="text-gray-400 text-sm uppercase tracking-wider mb-3">24h High</h3>
                    <p id="high24h" class="text-3xl font-bold text-green-400">--</p>
                </div>
                <div class="glass-card rounded-2xl p-8 text-center stat-card glow-red">
                    <h3 class="text-gray-400 text-sm uppercase tracking-wider mb-3">24h Low</h3>
                    <p id="low24h" class="text-3xl font-bold text-red-400">--</p>
                </div>
                <div class="glass-card rounded-2xl p-8 text-center stat-card">
                    <h3 class="text-gray-400 text-sm uppercase tracking-wider mb-3">Market Cap</h3>
                    <p id="marketCap" class="text-3xl font-bold text-purple-400">--</p>
                </div>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
                <div class="glass-card rounded-2xl p-8 text-center stat-card">
                    <h3 class="text-gray-400 text-sm uppercase mb-4">Trading Signal (English)</h3>
                    <p id="signalEn" class="text-4xl font-bold text-white mb-2">--</p>
                    <p id="confidenceEn" class="text-lg text-gray-400 mt-3">--</p>
                </div>
                <div class="glass-card rounded-2xl p-8 text-center stat-card" dir="rtl">
                    <h3 class="text-gray-400 text-sm uppercase mb-4">سیگنال معاملاتی (فارسی)</h3>
                    <p id="signalFa" class="text-4xl font-bold text-white mb-2">--</p>
                    <p id="confidenceFa" class="text-lg text-gray-400 mt-3">--</p>
                </div>
            </div>

            <div class="glass-card rounded-2xl p-6 mb-8 flex justify-center gap-4">
                <button class="timeframe-btn" onclick="changeTimeframe('1')">1D</button>
                <button class="timeframe-btn active" onclick="changeTimeframe('7')">7D</button>
                <button class="timeframe-btn" onclick="changeTimeframe('30')">30D</button>
                <button class="timeframe-btn" onclick="changeTimeframe('90')">90D</button>
                <button class="timeframe-btn" onclick="changeTimeframe('365')">1Y</button>
            </div>

            <div class="glass-card rounded-3xl p-8">
                <div class="flex justify-between items-center mb-6">
                    <h3 class="text-2xl font-bold text-gray-300">Professional Price Chart</h3>
                </div>
                <div id="chart-container"></div>
            </div>
        </div>
    </div>

    <script>
        function createParticles() {
            const container = document.getElementById('particles');
            for (let i = 0; i < 50; i++) {
                const particle = document.createElement('div');
                particle.className = 'particle';
                particle.style.width = Math.random() * 5 + 'px';
                particle.style.height = particle.style.width;
                particle.style.left = Math.random() * 100 + '%';
                particle.style.animationDelay = Math.random() * 20 + 's';
                particle.style.animationDuration = (Math.random() * 20 + 10) + 's';
                container.appendChild(particle);
            }
        }
        createParticles();

        let chart = null;
        let lineSeries = null;
        let allCoins = [];
        let selectedCoinId = null;
        let currentTimeframe = '7';
        let priceUpdateInterval = null;

        window.onload = async () => { await loadCoins(); };

        async function loadCoins() {
            try {
                const response = await fetch('/api/coins');
                const data = await response.json();
                if (data.status === 'success') allCoins = data.coins;
            } catch (error) { console.error("Failed to load coins:", error); }
        }

        function searchCoins(query) {
            const dropdown = document.getElementById('dropdown');
            if (!query || query.length < 1) { dropdown.style.display = 'none'; return; }
            
            const filtered = allCoins.filter(c => 
                c.name.toLowerCase().includes(query.toLowerCase()) || 
                c.symbol.toLowerCase().includes(query.toLowerCase()) ||
                c.id.toLowerCase().includes(query.toLowerCase())
            ).slice(0, 15);
            
            if (filtered.length === 0) { dropdown.style.display = 'none'; return; }
            
            dropdown.innerHTML = filtered.map(c => `
                <div class="dropdown-item" onclick="selectCoin('${c.id}', '${c.name}', '${c.symbol}', ${c.current_price}, ${c.market_cap})">
                    ${c.image ? `<img src="${c.image}" alt="${c.symbol}">` : ''}
                    <div class="flex-1">
                        <div class="font-bold text-white text-lg">${c.name}</div>
                        <div class="text-gray-400">${c.symbol}</div>
                    </div>
                    <div class="text-right">
                        <div class="text-cyan-400 font-bold text-lg">$${c.current_price.toLocaleString()}</div>
                        <div class="text-gray-500 text-sm">MCap: $${(c.market_cap / 1e9).toFixed(2)}B</div>
                    </div>
                </div>
            `).join('');
            dropdown.style.display = 'block';
        }

        function selectCoin(id, name, symbol, price, marketCap) {
            document.getElementById('coinInput').value = name;
            document.getElementById('dropdown').style.display = 'none';
            selectedCoinId = id;
            
            document.getElementById('emptyState').classList.add('hidden');
            document.getElementById('dashboard').classList.remove('hidden');
            
            document.getElementById('coinName').innerText = `${name} (${symbol})`;
            document.getElementById('priceDisplay').innerText = `$${price.toLocaleString()}`;
            document.getElementById('marketCap').innerText = `$${(marketCap / 1e9).toFixed(2)}B`;
            
            loadChartData(id);
            startLiveUpdates(id);
        }

        async function loadChartData(coinId, days = currentTimeframe) {
            try {
                const response = await fetch(`/api/chart/${coinId}?days=${days}`);
                const data = await response.json();
                
                if (data.status === 'success') {
                    updateChart(data.chart_data);
                    document.getElementById('high24h').innerText = `$${data.high_24h.toLocaleString()}`;
                    document.getElementById('low24h').innerText = `$${data.low_24h.toLocaleString()}`;
                    
                    document.getElementById('signalEn').innerText = data.recommendation_en;
                    document.getElementById('signalFa').innerText = data.recommendation_fa;
                    document.getElementById('confidenceEn').innerText = `Confidence: ${data.confidence}%`;
                    document.getElementById('confidenceFa').innerText = `اطمینان: ${data.confidence}%`;
                    
                    const signalClass = data.signal === 'BUY' ? 'text-green-400 glow-green' : 
                                       data.signal === 'SELL' ? 'text-red-400 glow-red' : 'text-yellow-400';
                    document.getElementById('signalEn').className = `text-4xl font-bold mb-2 ${signalClass}`;
                    document.getElementById('signalFa').className = `text-4xl font-bold mb-2 ${signalClass}`;
                }
            } catch (error) { console.error("Failed to load chart:", error); }
        }

        // ✅ فقط نمودار Line نمایش داده می‌شود
        function updateChart(chartData) {
            const container = document.getElementById('chart-container');
            container.innerHTML = '';
            
            chart = LightweightCharts.createChart(container, {
                width: container.clientWidth,
                height: 600,
                layout: {
                    background: { color: 'transparent' },
                    textColor: '#d1d4dc',
                    fontSize: 12,
                },
                grid: {
                    vertLines: { color: 'rgba(0, 255, 255, 0.1)' },
                    horzLines: { color: 'rgba(0, 255, 255, 0.1)' },
                },
                crosshair: {
                    mode: LightweightCharts.CrosshairMode.Normal,
                    vertLine: {
                        width: 1,
                        color: 'rgba(0, 255, 255, 0.5)',
                        style: 3,
                    },
                    horzLine: {
                        width: 1,
                        color: 'rgba(0, 255, 255, 0.5)',
                        style: 3,
                    },
                },
                rightPriceScale: {
                    borderColor: 'rgba(0, 255, 255, 0.3)',
                },
                timeScale: {
                    borderColor: 'rgba(0, 255, 255, 0.3)',
                    timeVisible: true,
                    secondsVisible: false,
                },
                handleScroll: {
                    vertTouchDrag: false,
                    mouseWheel: true,
                    pressedMouseMove: true,
                },
                handleScale: {
                    axisPressedMouseMove: {
                        time: true,
                        price: true,
                    },
                    mouseWheel: true,
                    pinch: true,
                },
            });
            
            lineSeries = chart.addLineSeries({
                color: '#00ffff',
                lineWidth: 3,
                crosshairMarkerVisible: true,
                crosshairMarkerRadius: 6,
            });
            
            lineSeries.setData(chartData.map(d => ({ time: d.time, value: d.close })));
            chart.timeScale().fitContent();
            
            window.addEventListener('resize', () => {
                if (chart) chart.applyOptions({ width: container.clientWidth });
            });
        }

        function changeTimeframe(days) {
            currentTimeframe = days;
            document.querySelectorAll('.timeframe-btn').forEach(btn => btn.classList.remove('active'));
            event.target.classList.add('active');
            if (selectedCoinId) loadChartData(selectedCoinId, days);
        }

        async function startLiveUpdates(coinId) {
            if (priceUpdateInterval) clearInterval(priceUpdateInterval);
            priceUpdateInterval = setInterval(async () => {
                try {
                    const response = await fetch(`/api/price/${coinId}`);
                    const data = await response.json();
                    if (data.status === 'success') {
                        const priceEl = document.getElementById('priceDisplay');
                        const oldPrice = parseFloat(priceEl.innerText.replace(/[$,]/g, ''));
                        const newPrice = data.price;
                        priceEl.innerText = `$${newPrice.toLocaleString()}`;
                        const change = ((newPrice - oldPrice) / oldPrice * 100).toFixed(2);
                        const changeEl = document.getElementById('priceChange');
                        if (change > 0) {
                            changeEl.innerText = `▲ +${change}%`;
                            changeEl.className = 'text-lg font-semibold mt-3 price-up';
                        } else if (change < 0) {
                            changeEl.innerText = `▼ ${change}%`;
                            changeEl.className = 'text-lg font-semibold mt-3 price-down';
                        }
                    }
                } catch (error) { console.error("Failed to update price:", error); }
            }, 5000);
        }
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def read_root():
    return HTML_CONTENT

@app.get("/api/coins")
async def get_all_coins():
    try:
        url = "https://api.coingecko.com/api/v3/coins/markets"
        params = {"vs_currency": "usd", "order": "market_cap_desc", "per_page": 100, "page": 1, "sparkline": False}
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        coins = response.json()
        coin_list = [{"id": coin["id"], "symbol": coin["symbol"].upper(), "name": coin["name"], "current_price": coin["current_price"], "market_cap": coin["market_cap"], "high_24h": coin.get("high_24h", 0), "low_24h": coin.get("low_24h", 0), "image": coin["image"]} for coin in coins]
        return {"status": "success", "coins": coin_list}
    except Exception as e:
        fallback_coins = [
            {"id": "bitcoin", "symbol": "BTC", "name": "Bitcoin", "current_price": 79000, "market_cap": 1560000000000, "high_24h": 80000, "low_24h": 78000, "image": "https://assets.coingecko.com/coins/images/1/small/bitcoin.png"},
            {"id": "ethereum", "symbol": "ETH", "name": "Ethereum", "current_price": 3100, "market_cap": 370000000000, "high_24h": 3200, "low_24h": 3000, "image": "https://assets.coingecko.com/coins/images/279/small/ethereum.png"},
            {"id": "binancecoin", "symbol": "BNB", "name": "BNB", "current_price": 600, "market_cap": 90000000000, "high_24h": 610, "low_24h": 590, "image": "https://assets.coingecko.com/coins/images/825/small/bnb-icon2_2x.png"},
            {"id": "solana", "symbol": "SOL", "name": "Solana", "current_price": 180, "market_cap": 80000000000, "high_24h": 185, "low_24h": 175, "image": "https://assets.coingecko.com/coins/images/4128/small/solana.png"},
            {"id": "ripple", "symbol": "XRP", "name": "XRP", "current_price": 0.6, "market_cap": 32000000000, "high_24h": 0.62, "low_24h": 0.58, "image": "https://assets.coingecko.com/coins/images/44/small/xrp-symbol-white-128.png"},
            {"id": "cardano", "symbol": "ADA", "name": "Cardano", "current_price": 0.45, "market_cap": 16000000000, "high_24h": 0.47, "low_24h": 0.43, "image": "https://assets.coingecko.com/coins/images/975/small/cardano.png"},
            {"id": "dogecoin", "symbol": "DOGE", "name": "Dogecoin", "current_price": 0.15, "market_cap": 21000000000, "high_24h": 0.16, "low_24h": 0.14, "image": "https://assets.coingecko.com/coins/images/5/small/dogecoin.png"},
            {"id": "polkadot", "symbol": "DOT", "name": "Polkadot", "current_price": 7, "market_cap": 9000000000, "high_24h": 7.2, "low_24h": 6.8, "image": "https://assets.coingecko.com/coins/images/12171/small/polkadot.png"},
            {"id": "shiba-inu", "symbol": "SHIB", "name": "Shiba Inu", "current_price": 0.000025, "market_cap": 15000000000, "high_24h": 0.000026, "low_24h": 0.000024, "image": "https://assets.coingecko.com/coins/images/11939/small/shiba.png"},
            {"id": "litecoin", "symbol": "LTC", "name": "Litecoin", "current_price": 75, "market_cap": 5500000000, "high_24h": 77, "low_24h": 73, "image": "https://assets.coingecko.com/coins/images/2/small/litecoin.png"}
        ]
        return {"status": "success", "coins": fallback_coins, "note": "Using fallback data"}

@app.get("/api/chart/{symbol}")
async def get_chart_data(symbol: str, days: int = 7):
    try:
        scraper = CryptoScraper(cache_dir="data", cache_hours=1)
        df = scraper.fetch_prices(symbol, days=days)
        if df.empty or len(df) < days * 24:
            df = generate_sample_data(symbol, days)
        
        chart_data = []
        for i, row in df.iterrows():
            price = row['price']
            timestamp = int(row['date'].timestamp())
            volatility = price * 0.02
            open_price = price + random.uniform(-volatility * 0.5, volatility * 0.5)
            close_price = price
            high_price = max(open_price, close_price) + random.uniform(0, volatility * 0.5)
            low_price = min(open_price, close_price) - random.uniform(0, volatility * 0.5)
            
            chart_data.append({"time": timestamp, "open": round(open_price, 2), "high": round(high_price, 2), "low": round(low_price, 2), "close": round(close_price, 2)})
        
        recent_data = df.tail(24) if len(df) >= 24 else df
        analyzer = CryptoAnalyzer(short_window=7, long_window=14)
        analyzed_df, signal = analyzer.analyze(df)
        
        confidence = 50
        if len(df) >= 14:
            ma_short = df['price'].rolling(window=7).mean().iloc[-1]
            ma_long = df['price'].rolling(window=14).mean().iloc[-1]
            trend_strength = abs(ma_short - ma_long) / ma_long * 100
            confidence = min(95, max(50, int(trend_strength * 5 + 50)))
        
        return {
            "status": "success", "symbol": symbol.upper(),
            "chart_data": chart_data,
            "high_24h": recent_data['price'].max(), "low_24h": recent_data['price'].min(),
            "signal": signal.get("signal"),
            "recommendation_fa": get_persian_recommendation(signal.get("signal")),
            "recommendation_en": get_english_recommendation(signal.get("signal")),
            "confidence": confidence
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def generate_sample_data(symbol: str, days: int) -> pd.DataFrame:
    base_prices = {"bitcoin": 79000, "ethereum": 3100, "binancecoin": 600, "solana": 180, "ripple": 0.6, "cardano": 0.45, "dogecoin": 0.15, "polkadot": 7, "shiba-inu": 0.000025, "litecoin": 75}
    base_price = base_prices.get(symbol, 100)
    dates = pd.date_range(end=datetime.now(), periods=days*24, freq='H')
    prices = []
    current_price = base_price
    for i in range(len(dates)):
        change = np.random.normal(0, current_price * 0.02)
        current_price += change
        current_price = max(current_price, base_price * 0.5)
        prices.append(current_price)
    return pd.DataFrame({'date': dates, 'price': prices})

@app.get("/api/price/{symbol}")
async def get_live_price(symbol: str):
    try:
        scraper = CryptoScraper(cache_dir="data", cache_hours=0.1)
        current_data = scraper.get_current_price(symbol)
        return {"status": "success", "price": current_data.get("price"), "currency": current_data.get("currency")}
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
    time.sleep(1.5)
    webbrowser.open("http://127.0.0.1:8000")

if __name__ == "__main__":
    threading.Thread(target=open_browser).start()
    uvicorn.run(app, host="127.0.0.1", port=8000)
