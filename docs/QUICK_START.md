# Quick Reference Guide

## 🚀 Getting Started (3 steps)

```bash
# 1. Activate virtual environment
.venv\Scripts\activate

# 2. Run backtest
python main.py

# 3. Select option from menu
# Recommended: Option 4 (Compare All Configs)
```

## 📋 Main Menu Options

| Option | Description | Use Case |
|--------|-------------|----------|
| **1** | Real BTC Data | Test with actual market data from Yahoo Finance |
| **2** | Simulated Crash | Test $60k → $13k crash scenarios |
| **3** | Custom CSV | Load your own OHLCV data |
| **4** | Compare All | Side-by-side comparison of all 4 configs |
| **5** | Exit | Close program |

## 🎯 Which Config to Use?

| Market Condition | Recommended Config | Why? |
|------------------|-------------------|------|
| **Sideway/Ranging** | ADAPTIVE (1.6% step) | +71.93% avg ROI, 100% win rate |
| **High Volatility** | SCALPING (1.2% step) | Captures quick moves |
| **Conservative/Uptrend** | CONSERVATIVE (2.5% step) | Lower risk, +25.70% Jan 2025 |
| **Aggressive** | AGGRESSIVE (1.5% step) | Higher risk/reward |
| **Not Sure?** | ADAPTIVE | Best all-around performer |

## 📊 Expected Performance

### ADAPTIVE Config (Recommended)
- **Sideway Markets**: +72% ROI ✅
- **Crash Scenarios**: +1.2M% theoretical (reduce 95% for reality) ⚠️
- **Uptrends**: +26% ROI ✅
- **Overall Win Rate**: 100% in tested sideway/crash conditions

### CONSERVATIVE Config
- **Jan 2025 Uptrend**: +25.70% ROI
- **Max Drawdown**: 6.93%
- **Good for**: Lower risk tolerance

## 🔧 Code Structure

```python
# Import configs
from configs.strategy_configs import CONFIGS

# Import core modules
from core.strategy import DynamicGridHedgeStrategy
from core.backtest import BacktestEngine
from core.performance import PerformanceAnalyzer

# Import utilities
from utils.data_loader import download_btc_data, load_csv_data, generate_crash_data
```

## 📁 File Organization

| Folder | Contains | Purpose |
|--------|----------|---------|
| `configs/` | strategy_configs.py | All strategy parameters |
| `core/` | strategy, backtest, performance, indicators | Main logic |
| `utils/` | data_loader.py | Data loading & generation |
| `docs/` | 8 markdown files | Complete documentation |

## 💡 Common Tasks

### Run Quick Test
```bash
python main.py
# Select: 4 (Compare All Configs)
# Uses default Jan 2025 data
```

### Test Specific Period
```bash
python main.py
# Select: 1 (Real BTC Data)
# Enter: 2025-01-01 to 2025-01-31
# Select: 2 (Compare all configs)
```

### Test Crash Scenario
```bash
python main.py
# Select: 2 (Simulated Crash)
# Select: 1 (Gradual crash 180 days)
# Select: 1 (Single config)
# Select: 1 (adaptive)
```

### Load Your Own Data
```bash
python main.py
# Select: 3 (Custom CSV)
# Enter: path/to/your/data.csv
# CSV format: timestamp, open, high, low, close, volume
```

## 📈 Interpreting Results

### Metrics Explained
- **ROI**: Total return on investment (%)
- **Max Drawdown**: Largest peak-to-trough decline (%)
- **Sharpe Ratio**: Risk-adjusted returns (higher = better)
- **Win Rate**: Percentage of profitable trades
- **Grid Profit**: Profit from spot grid trades
- **Hedge Profit**: Profit from futures hedge positions
- **Total Fees**: All Binance fees paid

### Good Results
✅ ROI > 10% (monthly)
✅ Max Drawdown < 15%
✅ Sharpe Ratio > 1.0
✅ Win Rate > 50%

### Warning Signs
⚠️ Max Drawdown > 25%
⚠️ Total Fees > 30% of profits
⚠️ Win Rate < 40%

## 🛠️ Troubleshooting

### "No trades executed"
- Grid step too wide for volatility
- Try ADAPTIVE or SCALPING config
- Check price range matches grid parameters

### Import errors
- Ensure virtual environment activated
- Check `__init__.py` files exist in folders
- Verify you're in isve_backtest/ directory

### Data download fails
- Check internet connection
- Yahoo Finance might be rate limiting
- Try again after a few minutes

### Charts not generating
- matplotlib might not be installed
- Run: `pip install matplotlib`
- Check disk space for saving .png files

## 📚 Documentation

| File | Content |
|------|---------|
| [README.md](README.md) | Project overview & setup |
| [docs/STRATEGY_DESIGN.md](docs/STRATEGY_DESIGN.md) | Complete strategy explanation |
| [docs/SIDEWAY_STRATEGY_FINAL.md](docs/SIDEWAY_STRATEGY_FINAL.md) | Sideway market optimization |
| [docs/CRASH_TEST_RESULTS.md](docs/CRASH_TEST_RESULTS.md) | Extreme scenario results |
| [docs/RESTRUCTURING_SUMMARY.md](docs/RESTRUCTURING_SUMMARY.md) | Before/after restructuring |

## 🎓 Key Insights

1. **Grid step must match volatility**: 1.6% optimal for BTC's typical 2-7% daily moves
2. **Rebalancing ≠ Losses**: Grid adjusts to EMA50 without closing positions
3. **High drawdown tolerance**: 29% max allows recovery from whipsaws
4. **Fees matter**: 0.1% spot + funding costs add up quickly
5. **Crash performance inflated**: Reduce theoretical ROI by 80-95% for reality

## ⚡ Power User Tips

### Batch Testing
Edit main.py to loop through multiple date ranges automatically

### Custom Configs
Add new configs to `configs/strategy_configs.py`:
```python
CONFIG_MYCONFIG = {
    'grid_step': 0.020,  # Your parameters
    # ... other settings
}
CONFIGS['myconfig'] = CONFIG_MYCONFIG
```

### Performance Analysis
Results saved to:
- `backtest_results_v2.png` - 6-chart performance visualization
- `entry_points_ohlc.png` - **NEW: Candlestick with entry/exit points** 📊
- `trade_history_v2.csv` - All trade details
- `equity_curve_v2.csv` - Equity over time

### Data Files
Generated data saved to:
- `btc_2025_hourly.csv` - Downloaded real data
- `crash_*.csv` - Simulated crash scenarios

---

**Need help?** Check [README.md](README.md) or documentation in `docs/`

**Version**: 2.0  
**Last Updated**: 2025-01-XX
