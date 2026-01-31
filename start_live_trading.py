"""
Start Live Trading Bot on Binance Testnet
"""
from src.binance_connector import BinanceTradingBot
from src.live_trading_bot import LiveGridHedgeBot
from src.telegram_notifier import TelegramNotifier
from binance_config import (
    USE_TESTNET,
    BINANCE_TESTNET_API_KEY,
    BINANCE_TESTNET_SECRET,
    BINANCE_API_KEY,
    BINANCE_SECRET,
    TELEGRAM_BOT_TOKEN,
    TELEGRAM_CHAT_ID,
    ENABLE_TELEGRAM,
    validate_config
)
from src.configs.strategy_configs import CONFIG_ADAPTIVE

def main():
    print("="*70)
    print("LIVE TRADING BOT - BINANCE")
    print("="*70)
    
    # Validate config
    if not validate_config():
        print("\n❌ Configuration invalid")
        return
    
    # Get credentials
    if USE_TESTNET:
        api_key = BINANCE_TESTNET_API_KEY
        api_secret = BINANCE_TESTNET_SECRET
        print("\n✅ Using TESTNET (safe)")
    else:
        api_key = BINANCE_API_KEY
        api_secret = BINANCE_SECRET
        print("\n⚠️ Using LIVE TRADING (real money!)")
        
        confirm = input("\nType 'START LIVE TRADING' to confirm: ")
        if confirm != "START LIVE TRADING":
            print("Cancelled")
            return
    
    # Trading parameters
    SYMBOL = 'BTCUSDT'
    CHECK_INTERVAL = 60  # seconds (1 minute)
    
    print(f"\n{'='*70}")
    print("CONFIGURATION")
    print(f"{'='*70}")
    print(f"Symbol: {SYMBOL}")
    print(f"Mode: {'TESTNET' if USE_TESTNET else 'LIVE TRADING'}")
    print(f"Check interval: {CHECK_INTERVAL} seconds")
    print(f"Strategy: ADAPTIVE")
    print(f"  Grid Step: {CONFIG_ADAPTIVE['grid_step']*100}%")
    print(f"  Take Profit: {CONFIG_ADAPTIVE['grid_take_profit']*100}%")
    print(f"  Max Drawdown: {CONFIG_ADAPTIVE['max_drawdown']*100}%")
    print(f"  Initial Capital: ${CONFIG_ADAPTIVE['initial_capital']:,}")
    
    # Confirm start
    print(f"\n{'='*70}")
    print("⚠️ IMPORTANT WARNINGS")
    print(f"{'='*70}")
    print("1. This bot will place REAL orders on Binance")
    print("2. Orders execute at market price (slippage possible)")
    print("3. Bot runs continuously until you press Ctrl+C")
    print("4. Monitor the bot closely, especially first hour")
    print("5. Start with small capital on testnet first")
    
    if USE_TESTNET:
        print("\n💡 You're on TESTNET - safe to experiment!")
    else:
        print("\n⚠️ LIVE MODE - Real money at risk!")
    
    response = input("\nType 'START' to begin trading: ")
    if response != "START":
        print("Cancelled")
        return
    
    # Initialize Binance connector
    print("\n📡 Connecting to Binance...")
    bot_connector = BinanceTradingBot(api_key, api_secret, testnet=USE_TESTNET)
    
    # Test connection
    if not bot_connector.test_connection():
        print("❌ Connection failed")
        return
    
    # Initialize Telegram (if enabled)
    telegram = None
    if ENABLE_TELEGRAM:
        if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
            print("\n⚠️ Telegram enabled but credentials missing!")
            print("Edit binance_config.py to add TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID")
        else:
            print("\n📱 Initializing Telegram notifications...")
            telegram = TelegramNotifier(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID)
            if telegram.test_connection():
                print("✅ Telegram connected")
            else:
                print("⚠️ Telegram connection failed, continuing without notifications")
                telegram = None
    
    # Initialize trading bot
    print("\n🤖 Initializing trading bot...")
    trading_bot = LiveGridHedgeBot(bot_connector, SYMBOL, CONFIG_ADAPTIVE, telegram)
    
    if not trading_bot.initialize():
        print("❌ Initialization failed")
        return
    
    # Start trading
    print("\n" + "="*70)
    print("🚀 STARTING LIVE TRADING")
    print("="*70)
    print("\n💡 TIP: Press Ctrl+C to stop the bot safely")
    print("="*70 + "\n")
    
    input("Press ENTER to start...")
    
    trading_bot.start(check_interval=CHECK_INTERVAL)

if __name__ == "__main__":
    main()
