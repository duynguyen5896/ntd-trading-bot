import os
import threading
import time
import requests
from flask import Flask, request
from src.binance_connector import BinanceTradingBot
from src.live_trading_bot import LiveGridHedgeBot
from src.telegram_notifier import TelegramNotifier
from binance_config import (
    USE_TESTNET,
    BINANCE_TESTNET_API_KEY, BINANCE_TESTNET_SECRET,
    BINANCE_API_KEY, BINANCE_SECRET,
    TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, ENABLE_TELEGRAM
)
from src.configs.strategy_configs import CONFIG_ADAPTIVE

app = Flask(__name__)

# Global bot instance
bot_instance = None
bot_thread = None
is_running = False
startup_error = None

def run_bot():
    """Function to run the bot in a separate thread"""
    global bot_instance, is_running, startup_error
    
    print("="*50)
    print("STARTING BOT BACKGROUND THREAD")
    print("="*50)
    
    # Credentials from env (already loaded by binance_config)
    if USE_TESTNET:
        api_key = BINANCE_TESTNET_API_KEY
        api_secret = BINANCE_TESTNET_SECRET
        print("Bot Mode: TESTNET")
    else:
        api_key = BINANCE_API_KEY
        api_secret = BINANCE_SECRET
        print("Bot Mode: LIVE TRADING")

    if not api_key or not api_secret:
        startup_error = "CRITICAL: API Keys missing! Check Render Environment Variables."
        print(f"❌ {startup_error}")
        return

    # Initialize Binance Connector
    bot_connector = BinanceTradingBot(api_key, api_secret, testnet=USE_TESTNET)
    if not bot_connector.test_connection():
        startup_error = "Connection to Binance failed! Check API Keys or IP Restrictions."
        print(f"❌ {startup_error}")
        return

    # Initialize Telegram
    telegram = None
    if ENABLE_TELEGRAM and TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
        telegram = TelegramNotifier(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID)
        telegram.send_message("🚀 Render Bot Starting...")

    # Initialize Trading Bot
    symbol = 'BTCUSDT'
    bot_instance = LiveGridHedgeBot(bot_connector, symbol, CONFIG_ADAPTIVE, telegram)
    
    try:
        if bot_instance.initialize():
            print("✅ Bot Initialized Successfully")
            is_running = True
            # Run loop
            bot_instance.start(check_interval=60)
        else:
            startup_error = "Bot Initialization Failed (Data download or balance check failed)"
            print(f"❌ {startup_error}")
    except Exception as e:
        startup_error = f"Exception during start: {str(e)}"
        print(f"❌ {startup_error}")

    return "OK", 200

@app.route('/api/data')
def api_data():
    """API endpoint for frontend polling"""
    if bot_instance:
        chart_data = bot_instance.get_chart_data()
        price = bot_instance.price_history[-1] if bot_instance.price_history else 0
        roi = ((bot_instance.equity - bot_instance.start_equity) / bot_instance.start_equity) * 100 if bot_instance.start_equity else 0
        
        # Format positions for table
        positions = []
        for buy_price, qty in bot_instance.grid_positions.items():
            pnl = (price - buy_price) * qty
            pnl_pct = ((price - buy_price) / buy_price) * 100
            positions.append({
                'price': buy_price,
                'qty': qty,
                'pnl': pnl,
                'pnl_pct': pnl_pct
            })
            
        return {
            'status': "RUNNING" if is_running else "STOPPED",
            'mode': 'TESTNET' if USE_TESTNET else 'LIVE',
            'price': price,
            'equity': bot_instance.equity,
            'roi': roi,
            'positions': positions,
            'chart': chart_data
        }
    return {}

@app.route('/')
def home():
    color = "green" if is_running else "red"
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Trading Bot Dashboard</title>
        <script src="https://unpkg.com/lightweight-charts@3.8.0/dist/lightweight-charts.standalone.production.js"></script>
        <style>
            body {{ font-family: -apple-system, system-ui, sans-serif; max-width: 1000px; margin: 0 auto; padding: 20px; background: #f4f4f9; }}
            .card {{ background: white; padding: 20px; border-radius: 12px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); margin-bottom: 20px; }}
            .status {{ font-weight: bold; }}
            h1, h2 {{ margin-top: 0; }}
            table {{ width: 100%; border-collapse: collapse; }}
            th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }}
            th {{ background: #f8f9fa; }}
            .value {{ font-family: monospace; font-size: 1.2em; }}
            .grid {{ display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 20px; }}
            .error-box {{ background: #fee; color: #c00; padding: 15px; border-radius: 8px; border: 1px solid #fcc; }}
            #chart {{ width: 100%; height: 400px; }}
        </style>
    </head>
    <body>
        <div class="card">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <h1>🤖 Trading Bot</h1>
                <span id="status-badge" class="status" style="font-size: 1.5em; color: {color}">● {"RUNNING" if is_running else "STOPPED"}</span>
            </div>
            <div class="grid">
                <div>
                    <p>Current Price</p>
                    <div id="price" class="value">Loading...</div>
                </div>
                 <div>
                    <p>Total Equity</p>
                    <div id="equity" class="value">Loading...</div>
                </div>
                <div>
                    <p>ROI</p>
                    <div id="roi" class="value">Loading...</div>
                </div>
            </div>
        </div>

        <div class="card">
            <h2>📈 Price Chart (1H)</h2>
            <div id="chart"></div>
        </div>

        <div class="card">
            <h2>📋 Open <b>Grid</b> Positions</h2>
            <table>
                <thead>
                    <tr>
                        <th>Entry Price</th>
                        <th>Quantity</th>
                        <th>PnL ($)</th>
                        <th>PnL (%)</th>
                    </tr>
                </thead>
                <tbody id="positions-table">
                    <tr><td colspan='4'>Loading...</td></tr>
                </tbody>
            </table>
        </div>

        <script>
            // Chart Setup
            const chartContainer = document.getElementById('chart');
            const chart = LightweightCharts.createChart(chartContainer, {{
                width: chartContainer.clientWidth,
                height: 400,
                layout: {{ backgroundColor: '#ffffff', textColor: '#333' }},
                grid: {{ vertLines: {{ color: '#eee' }}, horzLines: {{ color: '#eee' }} }},
            }});
            const candleSeries = chart.addCandlestickSeries();
            
            // State
            let gridLines = [];

            async function updateData() {{
                try {{
                    const res = await fetch('/api/data');
                    const data = await res.json();
                    
                    if (!data.status) return;

                    // Update DOM
                    document.getElementById('price').innerText = '$' + data.price.toLocaleString(undefined, {{minimumFractionDigits: 2}});
                    document.getElementById('equity').innerText = '$' + data.equity.toLocaleString(undefined, {{minimumFractionDigits: 2}});
                    
                    const roiElem = document.getElementById('roi');
                    roiElem.innerText = (data.roi >= 0 ? '+' : '') + data.roi.toFixed(2) + '%';
                    roiElem.style.color = data.roi >= 0 ? 'green' : 'red';
                    
                    // Update Positions Table
                    const tbody = document.getElementById('positions-table');
                    if (data.positions.length === 0) {{
                        tbody.innerHTML = "<tr><td colspan='4'>No open positions</td></tr>";
                    }} else {{
                        tbody.innerHTML = data.positions.map(p => `
                            <tr>
                                <td>$${{p.price.toLocaleString()}}</td>
                                <td>${{p.qty}}</td>
                                <td style="color: ${{p.pnl >= 0 ? 'green' : 'red'}}">$${{p.pnl.toFixed(2)}}</td>
                                <td style="color: ${{p.pnl_pct >= 0 ? 'green' : 'red'}}">${{p.pnl_pct.toFixed(2)}}%</td>
                            </tr>
                        `).join('');
                    }}

                    // Update Chart
                    if (data.chart && data.chart.candles) {{
                        candleSeries.setData(data.chart.candles);
                        
                        // Clear old grid lines
                        gridLines.forEach(l => candleSeries.removePriceLine(l));
                        gridLines = [];
                        
                        // Add new grid lines
                        if (data.chart.grid_lines) {{
                            data.chart.grid_lines.forEach(price => {{
                                const line = candleSeries.createPriceLine({{
                                    price: price,
                                    color: 'blue',
                                    lineWidth: 1,
                                    lineStyle: LightweightCharts.LineStyle.Dashed,
                                    axisLabelVisible: true,
                                    title: 'Grid',
                                }});
                                gridLines.push(line);
                            }});
                        }}
                    }}

                }} catch (e) {{
                    console.error("Fetch error:", e);
                }}
            }}

            // Initial Load & Polling
            updateData();
            setInterval(updateData, 2000); // Poll every 2 seconds
            
            // Resize handler
            window.addEventListener('resize', () => {{
                chart.applyOptions({{ width: chartContainer.clientWidth }});
            }});
        </script>
    </body>
    </html>
    """
    
    return html

@app.route('/webhook', methods=['POST'])
def webhook():
    """Handle incoming Telegram updates"""
    try:
        update = request.json
        if not update or 'message' not in update:
            return "OK", 200
            
        message = update['message']
        if 'text' not in message:
            return "OK", 200
            
        chat_id = message['chat']['id']
        text = message['text'].strip()
        
        # Verify authorized user
        if str(chat_id) != str(TELEGRAM_CHAT_ID):
            print(f"⚠️ Unauthorized command from {chat_id}")
            return "Unauthorized", 403

        # Command Handler
        if text == '/status':
            handle_status_command(chat_id)
        elif text == '/open_orders' or text == '/orders':
            handle_orders_command(chat_id)
        
        return "OK", 200
    except Exception as e:
        print(f"❌ Webhook error: {e}")
        return "Error", 500

@app.route('/set_webhook')
def set_webhook():
    """Utility to set webhook"""
    url = request.host_url + "webhook"
    # Ensure https
    if url.startswith("http://"):
        url = url.replace("http://", "https://")
        
    api_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/setWebhook?url={url}"
    response = requests.get(api_url)
    return f"Webhook set to {url}: {response.text}"

def handle_status_command(chat_id):
    """Handle /status"""
    global bot_instance
    if not bot_instance or not is_running:
        send_telegram_message(chat_id, "⚠️ Bot is not running.")
        return
        
    price = bot_instance.price_history[-1] if bot_instance.price_history else 0
    roi = ((bot_instance.equity - bot_instance.start_equity) / bot_instance.start_equity) * 100
    
    msg = f"📊 <b>Bot Status</b>\n"
    msg += f"Price: <code>${price:,.2f}</code>\n"
    msg += f"Equity: <code>${bot_instance.equity:,.2f}</code>\n"
    msg += f"ROI: <code>{roi:+.2f}%</code>\n"
    msg += f"Positions: <code>{len(bot_instance.grid_positions)}</code>"
    send_telegram_message(chat_id, msg)

def handle_orders_command(chat_id):
    """Handle /open_orders"""
    global bot_instance
    if not bot_instance:
        send_telegram_message(chat_id, "⚠️ Bot is not initialized.")
        return

    msg = "📋 <b>Open Positions (Grid)</b>\n\n"
    
    if not bot_instance.grid_positions:
        msg += "<i>No open grid positions.</i>"
    else:
        for price, qty in bot_instance.grid_positions.items():
            current_price = bot_instance.price_history[-1] if bot_instance.price_history else price
            pnl_pct = ((current_price - price) / price) * 100
            msg += f"• Buy: <code>${price:,.2f}</code> | Qty: <code>{qty}</code> | PnL: <code>{pnl_pct:+.2f}%</code>\n"
            
    send_telegram_message(chat_id, msg)

def send_telegram_message(chat_id, text):
    """Helper to send message directly"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    requests.post(url, json=payload)

@app.route('/health')
def health():
    return "OK", 200

def start_bot_thread():
    global bot_thread
    if bot_thread is None or not bot_thread.is_alive():
        bot_thread = threading.Thread(target=run_bot, daemon=True)
        bot_thread.start()

# Start bot immediately when app loads (for Gunicorn)
start_bot_thread()

if __name__ == '__main__':
    # Local dev run
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
