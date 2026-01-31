"""
Test Telegram Bot Connection
"""
from telegram_notifier import TelegramNotifier
from binance_config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, ENABLE_TELEGRAM

def main():
    print("="*70)
    print("TELEGRAM BOT CONNECTION TEST")
    print("="*70)
    
    if not ENABLE_TELEGRAM:
        print("\n⚠️ Telegram is disabled in config")
        print("Set ENABLE_TELEGRAM = True in binance_config.py")
        return
    
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("\n❌ Telegram credentials not configured")
        print("\nPlease edit binance_config.py:")
        print("TELEGRAM_BOT_TOKEN = 'your_bot_token'")
        print("TELEGRAM_CHAT_ID = 'your_chat_id' (or '-100xxx' for channel)")
        return
    
    print(f"\nBot Token: {TELEGRAM_BOT_TOKEN[:20]}...")
    print(f"Chat/Channel ID: {TELEGRAM_CHAT_ID}")
    
    print("\n" + "="*70)
    print("Testing connection...")
    print("="*70)
    
    telegram = TelegramNotifier(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID)
    
    try:
        if telegram.test_connection():
            print("\n✅ SUCCESS! Check your Telegram for test message.")
            
            # Test additional notifications
            print("\nTesting trade notification...")
            telegram.notify_trade('BUY', 'BTCUSDT', 0.001, 83000.0)
            
            print("\nTesting status notification...")
            telegram.notify_status('BTCUSDT', 10000.0, 0.0, 0, 0, 0.0)
            
            print("\n✅ All tests passed!")
            print("Check your Telegram channel/chat for 3 messages:")
            print("  1. Connection test message")
            print("  2. BUY trade notification")
            print("  3. Status report")
            
        else:
            print("\n❌ FAILED! Check error above.")
            print("\nCommon issues:")
            print("1. Wrong bot token")
            print("2. Wrong chat/channel ID")
            print("3. Bot not added to channel as admin")
            print("4. Channel ID missing '-100' prefix")
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        
        print("\n🔧 Troubleshooting:")
        print("1. Verify bot token from @BotFather")
        print("2. For channel: Must start with '-100'")
        print("3. Bot must be admin of channel with 'Post Messages' permission")
        print("4. Send a message in channel first")

if __name__ == "__main__":
    main()
