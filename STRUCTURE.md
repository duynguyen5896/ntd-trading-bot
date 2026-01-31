# 📁 Project Structure

```
isve_backtest/
│
├── 📁 src/                          # Source code chính
│   ├── binance_connector.py         # Binance API wrapper
│   ├── live_trading_bot.py          # Live trading bot logic
│   ├── telegram_notifier.py         # Telegram notifications
│   │
│   ├── 📁 configs/                  # Strategy configurations
│   │   ├── __init__.py
│   │   └── strategy_configs.py     # Grid/Hedge parameters
│   │
│   ├── 📁 core/                     # Core trading logic
│   │   ├── __init__.py
│   │   ├── indicators.py           # EMA, ATR, etc.
│   │   ├── strategy.py             # Grid + Hedge strategy
│   │   ├── backtest.py             # Backtesting engine
│   │   └── performance.py          # Metrics & reporting
│   │
│   └── 📁 utils/                    # Utilities
│       ├── __init__.py
│       └── logger.py               # Logging system
│
├── 📁 tests/                        # Test files
│   ├── test_binance_connection.py  # Test Binance API
│   ├── test_telegram.py            # Test Telegram bot
│   ├── test_6months.py             # BTC 6-month backtest
│   ├── test_gold_6months.py        # Gold backtest
│   ├── test_dji_6months.py         # DJI backtest
│   ├── test_vnindex_6months.py     # VNM backtest
│   ├── test_candlestick.py         # OHLC chart test
│   ├── test_markers.py             # Marker visibility test
│   └── diagnose_markers.py         # Debug markers
│
├── 📁 data/                         # Backtest data & results
│   ├── btc_2025_hourly.csv         # BTC price data
│   ├── crash_*.csv                 # Monte Carlo scenarios
│   ├── *.png                       # Chart outputs
│   ├── trade_history*.csv          # Backtest results
│   └── equity_curve*.csv           # Equity tracking
│
├── 📁 scripts/                      # Utility scripts
│   ├── run_bot.bat                 # Windows batch runner
│   └── cleanup.ps1                 # PowerShell cleanup
│
├── 📁 docs/                         # Documentation
│   ├── PYTHONANYWHERE_DEPLOY.md    # PythonAnywhere guide
│   ├── TELEGRAM_SETUP.md           # Telegram bot setup
│   ├── BINANCE_SETUP_GUIDE.md      # Binance API guide
│   └── QUICK_START.md              # Quick start guide
│
├── 📁 mt5_export/                   # MetaTrader 5 EA
│   ├── GridHedgeGold_EA.mq5        # MQL5 Expert Advisor
│   └── INSTALLATION_GUIDE.md       # MT5 install guide
│
├── binance_config.py                # API & Telegram config
├── start_live_trading.py            # 🚀 Main entry point
├── requirements.txt                 # Python dependencies
├── README.md                        # Main documentation
└── .gitignore                       # Git ignore rules

```

## 🚀 Quick Start

### Run Live Trading Bot:
```bash
python start_live_trading.py
```

### Run Backtests:
```bash
python tests/test_6months.py
python tests/test_gold_6months.py
```

### Test Connections:
```bash
python tests/test_binance_connection.py
python tests/test_telegram.py
```

## 📦 Key Files

| File | Description |
|------|-------------|
| **start_live_trading.py** | Main entry point for live trading |
| **binance_config.py** | API keys & Telegram configuration |
| **src/live_trading_bot.py** | Core bot logic (Grid + Hedge) |
| **src/binance_connector.py** | Binance API wrapper |
| **src/telegram_notifier.py** | Telegram notifications |
| **src/configs/strategy_configs.py** | Trading parameters |

## 🔧 Configuration

Edit `binance_config.py`:
```python
# Binance API
BINANCE_TESTNET_API_KEY = "your_testnet_key"
BINANCE_TESTNET_SECRET = "your_testnet_secret"

# Telegram
TELEGRAM_BOT_TOKEN = "your_bot_token"
TELEGRAM_CHAT_ID = "-100your_channel_id"
ENABLE_TELEGRAM = True
```

## 📊 Data Files

All backtest data and results stored in `data/`:
- CSV files: Price data, trade history
- PNG files: Charts and visualizations
- Monte Carlo scenarios for stress testing

## 🧪 Tests

All test files in `tests/`:
- Connection tests (Binance, Telegram)
- Backtests (6-month historical data)
- Chart visualization tests
- Marker debugging tools

## 📚 Documentation

Complete guides in `docs/`:
- Deployment (PythonAnywhere, Railway)
- Setup (Binance API, Telegram bot)
- Quick start tutorials
