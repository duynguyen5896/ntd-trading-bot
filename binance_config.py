"""
Binance API Configuration
IMPORTANT: NEVER commit .env file to git!
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ============================================================================
# BINANCE API CREDENTIALS
# ============================================================================
# Get your API keys from: https://www.binance.com/en/my/settings/api-management

# TESTNET (for practice - RECOMMENDED to start)
BINANCE_TESTNET_API_KEY = os.getenv("BINANCE_TESTNET_API_KEY")
BINANCE_TESTNET_SECRET = os.getenv("BINANCE_TESTNET_SECRET")
BINANCE_TESTNET_BASE_URL = os.getenv("BINANCE_TESTNET_BASE_URL", "https://testnet.binance.vision")

# LIVE TRADING (use with EXTREME caution)
BINANCE_API_KEY = os.getenv("BINANCE_API_KEY")
BINANCE_SECRET = os.getenv("BINANCE_SECRET")

# ============================================================================
# TELEGRAM NOTIFICATIONS
# ============================================================================
# Get bot token from @BotFather on Telegram
# Get chat ID from @userinfobot
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
ENABLE_TELEGRAM = True  # Set True to enable notifications

# ============================================================================
# TRADING CONFIGURATION
# ============================================================================
USE_TESTNET = True  # ALWAYS start with True!

# Trading pairs
TRADING_PAIRS = {
    'BTCUSDT': {
        'min_notional': 10,      # Minimum $10 per order
        'step_size': 0.00001,    # Price precision
        'quantity_precision': 5,
    },
    'ETHUSDT': {
        'min_notional': 10,
        'step_size': 0.01,
        'quantity_precision': 4,
    },
    'XAUUSD': {  # Gold (if available)
        'min_notional': 10,
        'step_size': 0.01,
        'quantity_precision': 3,
    }
}

# Risk Management
RISK_CONFIG = {
    'max_position_size': 0.1,      # Max 10% of capital per position
    'max_total_exposure': 0.5,     # Max 50% total capital in positions
    'max_drawdown_stop': 0.20,     # Stop all trading if DD > 20%
    'daily_loss_limit': 0.05,      # Stop if lose 5% in one day
}

# ============================================================================
# SAFETY CHECKS
# ============================================================================
def validate_config():
    """Validate configuration before trading"""
    errors = []
    
    if USE_TESTNET:
        if not BINANCE_TESTNET_API_KEY or not BINANCE_TESTNET_SECRET:
            errors.append("❌ Testnet API credentials not found in .env!")
    else:
        if not BINANCE_API_KEY or not BINANCE_SECRET:
            errors.append("❌ Live API credentials not found in .env!")
        
        # Extra warnings for live trading
        print("⚠️" * 20)
        print("WARNING: LIVE TRADING MODE ENABLED!")
        print("⚠️" * 20)
        response = input("Type 'I UNDERSTAND THE RISKS' to continue: ")
        if response != "I UNDERSTAND THE RISKS":
            errors.append("Live trading not confirmed")
    
    if errors:
        print("\n".join(errors))
        return False
    
    return True

# ============================================================================
# HOW TO GET API KEYS
# ============================================================================
"""
TESTNET (Recommended for beginners):
1. Go to: https://testnet.binance.vision/
2. Click "Generate HMAC_SHA256 Key"
3. Copy API Key and Secret Key
4. Add to .env file:
   BINANCE_TESTNET_API_KEY=your_key
   BINANCE_TESTNET_SECRET=your_secret

LIVE TRADING (Use with caution):
1. Go to: https://www.binance.com/en/my/settings/api-management
2. Create API Key
3. Enable "Spot & Margin Trading" (NOT Futures initially)
4. Whitelist your IP address
5. Set restrictions: 
   - Enable Spot Trading only
   - Disable Withdrawals (for safety)
6. Copy API Key and Secret
7. Add to .env file

SECURITY TIPS:
- Never share your API keys
- Never commit .env file to git
- Use .gitignore to exclude .env
- Enable IP whitelist
- Disable withdrawals on API key
- Start with small capital
- Test on TESTNET first!
"""
