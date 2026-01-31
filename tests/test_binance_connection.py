"""
Test Binance connection and basic trading functions
"""
from binance_connector import BinanceTradingBot
from binance_config import (
    USE_TESTNET, 
    BINANCE_TESTNET_API_KEY, 
    BINANCE_TESTNET_SECRET,
    BINANCE_API_KEY,
    BINANCE_SECRET,
    validate_config
)

def main():
    print("="*70)
    print("BINANCE CONNECTION TEST")
    print("="*70)
    
    # Validate configuration
    if not validate_config():
        print("\n❌ Configuration invalid. Please check binance_config.py")
        return
    
    # Get API credentials
    if USE_TESTNET:
        api_key = BINANCE_TESTNET_API_KEY
        api_secret = BINANCE_TESTNET_SECRET
        print("\n✅ Using TESTNET (safe for testing)")
    else:
        api_key = BINANCE_API_KEY
        api_secret = BINANCE_SECRET
        print("\n⚠️ Using LIVE TRADING (real money!)")
    
    # Check credentials
    if not api_key or not api_secret:
        print("\n❌ API credentials not configured!")
        print("\nPlease edit binance_config.py and add your API key/secret")
        print("\nHow to get API keys:")
        print("1. TESTNET: https://testnet.binance.vision/")
        print("2. LIVE: https://www.binance.com/en/my/settings/api-management")
        return
    
    # Initialize bot
    try:
        bot = BinanceTradingBot(api_key, api_secret, testnet=USE_TESTNET)
    except Exception as e:
        print(f"\n❌ Failed to initialize bot: {e}")
        return
    
    # Test connection
    print("\n" + "="*70)
    print("Testing connection...")
    print("="*70)
    
    if not bot.test_connection():
        print("\n❌ Connection test failed!")
        return
    
    # Get current prices
    print("\n" + "="*70)
    print("Current Prices:")
    print("="*70)
    
    symbols = ['BTCUSDT', 'ETHUSDT']
    for symbol in symbols:
        price = bot.get_price(symbol)
        if price > 0:
            print(f"{symbol}: ${price:,.2f}")
    
    # Download historical data
    print("\n" + "="*70)
    print("Historical Data Test:")
    print("="*70)
    
    df = bot.get_historical_data('BTCUSDT', interval='1h', days=7)
    
    if not df.empty:
        print(f"\n✅ Downloaded {len(df)} bars")
        print(f"Date range: {df.index[0]} to {df.index[-1]}")
        print(f"Price range: ${df['close'].min():,.2f} - ${df['close'].max():,.2f}")
        print(f"\nLast 5 bars:")
        print(df[['open', 'high', 'low', 'close']].tail())
    
    # Check open orders
    print("\n" + "="*70)
    print("Open Orders:")
    print("="*70)
    
    open_orders = bot.get_open_orders()
    if open_orders:
        for order in open_orders:
            print(f"Order {order['orderId']}: {order['side']} {order['origQty']} {order['symbol']} @ {order['price']}")
    else:
        print("No open orders")
    
    print("\n" + "="*70)
    print("✅ ALL TESTS PASSED!")
    print("="*70)
    
    print("\n🎯 Next Steps:")
    print("1. Check your balances above")
    print("2. Review historical data download")
    print("3. Ready to run backtests with real data")
    print("4. To trade live: Implement strategy in binance_live_trader.py")
    
    if USE_TESTNET:
        print("\n💡 TIP: You're on TESTNET - safe to experiment!")
        print("Get testnet funds: https://testnet.binance.vision/")
    else:
        print("\n⚠️ WARNING: LIVE TRADING MODE")
        print("Start with small amounts and monitor closely!")

if __name__ == "__main__":
    main()
