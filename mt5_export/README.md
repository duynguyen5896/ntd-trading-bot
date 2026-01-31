# Grid + Hedge EA for MetaTrader 5

Expert Advisor (EA) cho MT5 để trade vàng (XAUUSD) với chiến lược Grid + Hedge đã được backtest trên Python.

## 📦 Package Contents

```
mt5_export/
├── GridHedgeGold_EA.mq5        # Main EA file (MQL5 code)
├── INSTALLATION_GUIDE.md       # Hướng dẫn chi tiết
├── Config_ADAPTIVE.set         # ADAPTIVE config (recommended)
├── Config_CONSERVATIVE.set     # CONSERVATIVE config
├── Config_SCALPING.set         # SCALPING config
└── README.md                   # File này
```

## 🚀 Quick Start

### 1. Cài đặt nhanh
```
1. Copy GridHedgeGold_EA.mq5 vào MT5/MQL5/Experts/
2. Compile trong MetaEditor (F7)
3. Kéo EA vào chart XAUUSD H1
4. Load config: Config_ADAPTIVE.set
5. Click OK để bắt đầu
```

### 2. Settings mặc định (ADAPTIVE)
- Grid Step: **1.6%**
- Take Profit: **2.4%**
- Max Drawdown: **29%**
- Hedge Trigger: **2.5 ATR**

## 📊 Chiến lược

### Grid Trading
- Mua khi giá < EMA50 (grid steps 1.6%)
- Bán khi profit > 2.4%
- Tự động rebalance grid theo EMA

### Hedge Protection
- Mở SELL hedge khi giá xa EMA > 2.5 ATR
- Đóng hedge khi giá về gần EMA
- Bảo vệ vốn trong downtrend

## 🎯 Hiệu suất (từ Python backtest)

| Điều kiện | ROI | Win Rate | Drawdown |
|-----------|-----|----------|----------|
| Sideway | +72% | 100% | -15% |
| Downtrend -27% | +66,853%* | 100% | -28% |
| Uptrend | +26% | 100% | -7% |

*ROI lý thuyết, thực tế giảm 80-95%

## 📋 Configs có sẵn

### ADAPTIVE (Khuyến nghị)
- **Best for**: Tất cả điều kiện thị trường
- Grid: 1.6%, TP: 2.4%
- ROI trung bình: +72% (sideway)

### CONSERVATIVE
- **Best for**: Trader mới, rủi ro thấp
- Grid: 2.5%, TP: 3.5%
- ROI ổn định, drawdown thấp

### SCALPING
- **Best for**: Thị trường volatile
- Grid: 1.2%, TP: 1.8%
- Nhiều trades, ROI cao ngắn hạn

## ⚙️ Requirements

- **MT5**: Build 3661+
- **Symbol**: XAUUSD (Gold)
- **Timeframe**: H1 (1 hour)
- **Vốn tối thiểu**: $1,000 (demo), $5,000 (real)
- **Margin**: Free margin > 50%

## ⚠️ Rủi ro

1. **Max Drawdown 29%**: EA sẽ stop khi drawdown quá cao
2. **Margin Call**: Đảm bảo đủ margin cho grid + hedge
3. **Spread**: EA chỉ trade khi spread < 0.5 USD
4. **Slippage**: Kết quả thực có thể khác backtest 10-20%

## 🔧 Customization

### Tham số có thể điều chỉnh

**Grid:**
- Grid Step (1.2% - 2.5%)
- Take Profit (1.8% - 3.5%)
- Max Levels (5 - 15)

**Hedge:**
- Trigger ATR (2.0 - 3.0)
- Hedge Size (10% - 20%)
- Leverage (1 - 3)

**Risk:**
- Max Drawdown (20% - 35%)
- Max Spread (0.3 - 1.0 USD)

## 📈 Optimization Guide

### Strategy Tester
1. Symbol: XAUUSD
2. Period: H1
3. Dates: 6 months recent
4. Optimize: Grid Step + Take Profit
5. Criteria: Max ROI với Drawdown < 25%

### Forward Test
- Test demo 2-4 tuần
- So sánh với backtest results
- Chấp nhận nếu ROI > 50% expected

## 📚 Documentation

Xem **INSTALLATION_GUIDE.md** cho:
- Hướng dẫn cài đặt chi tiết
- Cấu hình parameters
- Troubleshooting
- Monitoring & logs
- Performance metrics

## 🎓 Best Practices

### Trước khi Live
- [ ] Test demo ít nhất 2 tuần
- [ ] Optimize cho symbol XAUUSD
- [ ] Forward test 1 tháng
- [ ] Hiểu rõ risk management
- [ ] Monitor hàng ngày

### Khi Live
- Check equity mỗi ngày
- Theo dõi drawdown
- Adjust parameters nếu market thay đổi
- Stop nếu win rate < 40%

## 🐛 Known Issues

1. **Hedge không đóng**: Chờ price về EMA hoặc đóng manual
2. **Quá nhiều grid levels**: Tăng Grid Step
3. **Spread rejection**: Giảm Max Spread parameter

## 📞 Support

**Logs location:**
- Journal: Ctrl+T → Journal tab
- Experts: Ctrl+T → Experts tab
- Chart: Comment hiển thị real-time status

**Debug mode:**
- Enable trong code: `#define DEBUG_MODE`
- Recompile để xem logs chi tiết

## 🔄 Updates

### Version 1.0 (2026-01-31)
- Initial release
- Grid + Hedge strategy from Python
- 3 preset configs (ADAPTIVE, CONSERVATIVE, SCALPING)
- Full risk management
- MT5 compatible

### Planned
- Multi-symbol support (BTCUSD, EURUSD)
- Trailing stop for hedge
- Dynamic grid step based on volatility
- Web dashboard for monitoring

## 📄 License

MIT License - Sử dụng tự do, không bảo hành.

## ⚖️ Disclaimer

**TRADING CÓ RỦI RO**

- Không đảm bảo lợi nhuận
- Có thể mất toàn bộ vốn
- Backtest ≠ Kết quả thực tế
- Test Demo trước khi Live
- Chỉ trade với tiền bạn có thể mất

---

**Author**: Grid Hedge Strategy Team  
**Based on**: Python backtest framework  
**Version**: 1.0  
**Date**: 2026-01-31  
**Contact**: See INSTALLATION_GUIDE.md
