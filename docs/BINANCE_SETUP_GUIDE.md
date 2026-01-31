# ============================================================================
# BINANCE INTEGRATION - SETUP GUIDE
# ============================================================================

## 📋 Prerequisites

1. **Python packages cần cài đặt:**
```bash
pip install python-binance
```

2. **Binance Account:**
   - Testnet (recommended): https://testnet.binance.vision/
   - Live: https://www.binance.com/

## 🔑 Step 1: Lấy API Keys

### TESTNET (Khuyến nghị cho người mới):

1. Vào: https://testnet.binance.vision/
2. Click **"Generate HMAC_SHA256 Key"**
3. Copy **API Key** và **Secret Key**
4. Lưu lại an toàn

**Testnet funds (tiền ảo):**
- Vào https://testnet.binance.vision/
- Request test funds (BTC, ETH, USDT miễn phí)

### LIVE TRADING (Cẩn thận!):

1. Vào: https://www.binance.com/en/my/settings/api-management
2. Click **"Create API"**
3. Chọn tên (ví dụ: "GridHedgeBot")
4. Complete security verification (2FA, email)
5. **QUAN TRỌNG - Cấu hình bảo mật:**
   - ✅ Enable: **Spot & Margin Trading**
   - ❌ Disable: **Futures** (ban đầu)
   - ❌ Disable: **Withdrawals** (an toàn)
   - ✅ Enable: **IP Whitelist** (recommended)
6. Copy API Key và Secret Key
7. **KHÔNG BAO GIỜ chia sẻ keys!**

## ⚙️ Step 2: Cấu hình API Keys

Edit file `binance_config.py`:

```python
# TESTNET
BINANCE_TESTNET_API_KEY = "your_testnet_api_key_here"
BINANCE_TESTNET_SECRET = "your_testnet_secret_here"

# LIVE (sau khi test xong)
BINANCE_API_KEY = "your_live_api_key_here"
BINANCE_SECRET = "your_live_secret_here"

# Chọn mode
USE_TESTNET = True  # True = Testnet, False = Live
```

## 🧪 Step 3: Test Connection

```bash
python test_binance_connection.py
```

Kết quả mong đợi:
```
✅ Connected to Binance TESTNET
Status: normal
Can Trade: True
💰 Account Balances:
  USDT: 100000.00000000
  BTC: 10.00000000
✅ ALL TESTS PASSED!
```

## 📊 Step 4: Download Data & Backtest

```python
from binance_connector import BinanceTradingBot
from binance_config import BINANCE_TESTNET_API_KEY, BINANCE_TESTNET_SECRET

# Initialize
bot = BinanceTradingBot(
    BINANCE_TESTNET_API_KEY, 
    BINANCE_TESTNET_SECRET, 
    testnet=True
)

# Download data
df = bot.get_historical_data('BTCUSDT', interval='1h', days=180)

# Run backtest với data thật từ Binance
from configs.strategy_configs import CONFIG_ADAPTIVE
from core.strategy import DynamicGridHedgeStrategy
from core.backtest import BacktestEngine

strategy = DynamicGridHedgeStrategy(CONFIG_ADAPTIVE)
engine = BacktestEngine(strategy, df, CONFIG_ADAPTIVE)
results = engine.run()
```

## 🤖 Step 5: Live Trading (Thận trọng!)

**TRƯỚC KHI LIVE:**
- ✅ Backtest thành công trên TESTNET
- ✅ Paper trade ít nhất 2 tuần
- ✅ Win rate > 60%
- ✅ Drawdown < 25%
- ✅ Hiểu rõ risk management
- ✅ Bắt đầu với capital nhỏ ($100-500)

**Live Trading Script:** (tạo sau khi backtest OK)

```python
from binance_connector import BinanceTradingBot
from binance_config import BINANCE_API_KEY, BINANCE_SECRET

# ⚠️ LIVE MODE
bot = BinanceTradingBot(BINANCE_API_KEY, BINANCE_SECRET, testnet=False)

# Check balance
balance = bot.get_account_balance('USDT')
print(f"Available: ${balance:.2f} USDT")

# Place order (example - don't run blindly!)
# bot.place_market_order('BTCUSDT', 'BUY', 0.001)
```

## 🛡️ Security Best Practices

1. **API Key Settings:**
   - ✅ Enable IP Whitelist
   - ❌ Disable Withdrawals
   - ✅ Enable only Spot Trading (initially)
   - ✅ Use 2FA on account

2. **Code Security:**
   - ❌ NEVER commit `binance_config.py` to git
   - ✅ Add to `.gitignore`
   - ❌ NEVER share API keys
   - ✅ Rotate keys monthly

3. **Risk Management:**
   - Start with TESTNET
   - Paper trade 2-4 weeks
   - Start live with small capital
   - Set max drawdown limits
   - Monitor daily

## 📁 Files Created

```
isve_backtest/
├── binance_config.py          # ⚠️ API keys (add to .gitignore!)
├── binance_connector.py       # Binance API wrapper
├── test_binance_connection.py # Connection test script
└── BINANCE_SETUP_GUIDE.md    # This file
```

## 🚨 Common Issues

### 1. "API credentials not configured"
- Edit `binance_config.py` với API keys của bạn

### 2. "Signature verification failed"
- Check API key/secret đúng chưa
- Thử generate lại keys

### 3. "Invalid IP"
- Disable IP whitelist hoặc
- Add IP của bạn vào whitelist

### 4. "Insufficient balance"
- Testnet: Request more test funds
- Live: Deposit USDT

### 5. "Permission denied"
- Check API key có enable Spot Trading không
- Verify API key chưa expire

## 📞 Support

**Binance Testnet:**
- https://testnet.binance.vision/

**Binance API Docs:**
- https://binance-docs.github.io/apidocs/spot/en/

**Python Binance:**
- https://python-binance.readthedocs.io/

## ✅ Checklist

- [ ] Cài đặt `python-binance`
- [ ] Tạo Binance testnet account
- [ ] Generate API keys
- [ ] Cấu hình `binance_config.py`
- [ ] Run `test_binance_connection.py` thành công
- [ ] Download historical data
- [ ] Backtest với real Binance data
- [ ] Paper trade 2-4 tuần
- [ ] (Optional) Setup live trading với capital nhỏ

## 🎯 Next Steps

1. **Ngay bây giờ:**
   ```bash
   pip install python-binance
   python test_binance_connection.py
   ```

2. **Sau khi connection OK:**
   - Download 6 tháng BTC data từ Binance
   - Run backtest với ADAPTIVE config
   - So sánh với Yahoo Finance data

3. **Khi backtest profitable:**
   - Paper trade trên Testnet
   - Monitor performance
   - Optimize parameters

4. **Khi ready for live:**
   - Bắt đầu với $100-500
   - Trade 1 pair (BTCUSDT)
   - Monitor hàng ngày
   - Scale dần dần

---

**⚠️ DISCLAIMER:**
Trading cryptocurrencies involves significant risk. This bot is for educational purposes. Always test thoroughly on TESTNET before using real money. Never invest more than you can afford to lose.
