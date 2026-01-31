import os
import threading
import time
from flask import Flask
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

def run_bot():
    """Function to run the bot in a separate thread"""
    global bot_instance, is_running
    
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
        print("❌ CRITICAL: API Keys missing! Bot will not start.")
        return

    # Initialize Binance Connector
    bot_connector = BinanceTradingBot(api_key, api_secret, testnet=USE_TESTNET)
    if not bot_connector.test_connection():
        print("❌ Connection to Binance failed!")
        return

    # Initialize Telegram
    telegram = None
    if ENABLE_TELEGRAM and TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
        telegram = TelegramNotifier(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID)
        telegram.send_message("🚀 Render Bot Starting...")

    # Initialize Trading Bot
    symbol = 'BTCUSDT'
    bot_instance = LiveGridHedgeBot(bot_connector, symbol, CONFIG_ADAPTIVE, telegram)
    
    if bot_instance.initialize():
        print("✅ Bot Initialized Successfully")
        is_running = True
        # Run loop
        bot_instance.start(check_interval=60)
    else:
        print("❌ Bot Initialization Failed")

@app.route('/')
def home():
    status = "RUNNING" if is_running else "STOPPED"
    return f"<h1>Trading Bot Status: {status}</h1><p>Mode: {'TESTNET' if USE_TESTNET else 'LIVE'}</p>"

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
