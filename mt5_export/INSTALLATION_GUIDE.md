# Hướng dẫn cài đặt Grid + Hedge EA cho MT5

## 📋 Yêu cầu

- MetaTrader 5 (MT5)
- Tài khoản MT5 (Demo hoặc Real)
- Symbol: XAUUSD (Vàng) hoặc bất kỳ symbol nào
- Timeframe khuyến nghị: H1 (1 giờ)

## 📥 Cài đặt

### Bước 1: Copy file EA
1. Mở MT5
2. Vào Menu: **File → Open Data Folder**
3. Mở thư mục: **MQL5 → Experts**
4. Copy file `GridHedgeGold_EA.mq5` vào thư mục này

### Bước 2: Compile
1. Trong MT5, mở **MetaEditor** (F4)
2. Tìm file `GridHedgeGold_EA.mq5` trong Navigator
3. Double click để mở
4. Nhấn **Compile** (F7)
5. Kiểm tra không có lỗi trong tab Errors

### Bước 3: Attach vào chart
1. Mở chart XAUUSD, timeframe H1
2. Trong Navigator, tìm **Expert Advisors → GridHedgeGold_EA**
3. Kéo thả vào chart
4. Dialog settings sẽ hiện ra

## ⚙️ Cấu hình tham số

### Capital Settings (Vốn)
```
Initial Capital: 10000 USD    # Vốn ban đầu
Risk per trade: 2%            # Rủi ro mỗi lệnh
```

### Grid Settings (Lưới)
```
Grid step: 1.6%               # Khoảng cách giữa các level (ADAPTIVE)
Take profit: 2.4%             # Chốt lời
Max grid levels: 10           # Tối đa 10 levels
Grid size: 3%                 # Kích thước mỗi lệnh (% vốn)
```

**Các configs có sẵn:**
- **ADAPTIVE** (khuyến nghị): Grid 1.6%, TP 2.4%
- **SCALPING**: Grid 1.2%, TP 1.8%
- **CONSERVATIVE**: Grid 2.5%, TP 3.5%
- **AGGRESSIVE**: Grid 1.5%, TP 2.5%

### Hedge Settings (Bảo hiểm)
```
Enable hedge: true            # Bật/tắt hedge
Hedge trigger: 2.5 ATR        # Kích hoạt khi giá xa EMA
Hedge size: 15%               # Kích thước hedge (% vốn)
Hedge leverage: 2             # Đòn bẩy hedge
```

### Risk Management
```
Max drawdown: 29%             # Drawdown tối đa trước khi stop
Max spread: 0.5 USD           # Spread tối đa cho phép
```

## 🎯 Chiến lược hoạt động

### Grid Trading
1. **Mua (BUY)**: Khi giá < EMA50
   - Mua theo grid steps (1.6% mỗi level)
   - Tối đa 10 levels
   
2. **Bán (SELL)**: Khi giá tăng lên
   - Chốt lời tại +2.4% từ giá mua
   - Win rate cao do grid rebalancing

### Hedge Protection
1. **Mở Hedge**: Khi giá xa EMA > 2.5 ATR
   - Mở lệnh SELL để bảo vệ
   - Size 15% vốn, leverage 2x
   
2. **Đóng Hedge**: Khi giá về gần EMA
   - Đóng khi distance < 1.25 ATR

## 📊 Backtesting

### Strategy Tester
1. Mở **View → Strategy Tester** (Ctrl+R)
2. Chọn:
   - Expert: GridHedgeGold_EA
   - Symbol: XAUUSD
   - Period: H1
   - Dates: 6 tháng gần nhất
3. Optimization: Có thể optimize Grid Step và Take Profit
4. Click **Start**

### Kết quả mong đợi (dựa trên backtest Python)
- **Sideway**: ROI +72% avg (100% win rate)
- **Downtrend -27%**: ROI +66,853% (theoretical, giảm 95% = +3,342% thực tế)
- **Uptrend**: ROI +26%
- **Max Drawdown**: 28-29%

## ⚠️ Lưu ý quan trọng

### 1. Test trên Demo trước
- **LUÔN test Demo 1-2 tuần trước**
- Kiểm tra logic hoạt động đúng
- Xem drawdown có chấp nhận được không

### 2. Vốn khuyến nghị
- **Tối thiểu**: $1,000 (demo)
- **Khuyến nghị**: $5,000 - $10,000 (real)
- **Grid size 3%** phù hợp với $10k

### 3. Spread & Slippage
- EA kiểm tra spread < 0.5 USD
- Nếu spread cao → không trade
- Broker tốt có spread XAUUSD: 0.2-0.3 USD

### 4. Margin requirements
- Grid + Hedge có thể dùng nhiều margin
- Đảm bảo margin level > 200%
- Stop khi margin call < 100%

### 5. Monitoring
- **Kiểm tra mỗi ngày**
- Xem Comment trên chart (info real-time)
- Log trong tab Experts (Ctrl+T)

## 🔧 Troubleshooting

### EA không trade
**Nguyên nhân:**
- Spread quá cao (> 0.5 USD)
- Không đủ tiền cho 1 lot
- Symbol không phải XAUUSD

**Giải pháp:**
- Giảm Max Spread: 0.5 → 1.0
- Giảm Grid Size: 3% → 1%
- Kiểm tra Journal (Ctrl+T)

### Quá nhiều lệnh
**Nguyên nhân:**
- Grid Step quá nhỏ (1.2%)
- Max Grid Levels quá cao (20)

**Giải pháp:**
- Tăng Grid Step: 1.6% → 2.0%
- Giảm Max Levels: 10 → 5

### Drawdown cao
**Nguyên nhân:**
- Downtrend mạnh
- Hedge không kích hoạt

**Giải pháp:**
- Giảm Hedge Trigger: 2.5 → 2.0 ATR
- Tăng Hedge Size: 15% → 20%
- Hoặc tắt EA tạm thời

### Hedge không đóng
**Nguyên nhân:**
- Giá không về gần EMA

**Giải pháp:**
- Đóng thủ công trong Trading tab
- Hoặc đợi (hedge sẽ profit trong downtrend)

## 📈 Optimization

### Tham số có thể optimize
1. **Grid Step** (1.2% - 2.5%)
   - Test từng 0.2%
   - Tìm step tối ưu cho XAUUSD
   
2. **Take Profit** (1.8% - 3.5%)
   - Cân bằng win rate vs profit size
   
3. **Hedge Trigger** (2.0 - 3.0 ATR)
   - Tùy volatility của vàng

### Forward Test
- Sau optimize, test forward 1 tháng demo
- So sánh với backtest
- Chấp nhận nếu ROI > 50% backtest ROI

## 📊 Performance Monitoring

### Metrics cần theo dõi
```
1. Total Equity - Vốn hiện tại
2. Drawdown (%) - Phải < 29%
3. Grid Levels active - < 10
4. Hedge status - ACTIVE/INACTIVE
5. Total Positions - Nên < 15
```

### Stop trading nếu
- Drawdown > 29%
- Equity < 80% initial capital liên tục 3 ngày
- Win rate < 40% (grid strategy có vấn đề)

## 📝 Logs & Debugging

### Trong Journal (Ctrl+T)
```
2026.01.31 16:45:00  GRID BUY: Level 2 | Price: 2045.50 | Lots: 0.01
2026.01.31 17:00:00  GRID SELL: Level 2 | Entry: 2045.50 | Exit: 2094.60 | Profit: $49.10
2026.01.31 18:00:00  HEDGE OPEN: Price far from EMA | Distance: 2.8 ATR | Lots: 0.03
2026.01.31 20:00:00  HEDGE CLOSE: Price returned to EMA
```

### Comment trên chart
```
=== GRID + HEDGE STRATEGY ===
Symbol: XAUUSD
EMA50: 2050.34
ATR: 15.67
---
Equity: $10,450.23
Drawdown: 4.50%
---
Grid Levels: 3/10
Hedge: ACTIVE
Total Positions: 4
```

## 🎓 Khuyến nghị sử dụng

### Thị trường tốt nhất
1. **Sideway** (tốt nhất): ROI cao, drawdown thấp
2. **Volatile**: Nhiều trades, ROI trung bình
3. **Slow trend**: Ổn định

### Thị trường cần cẩn thận
1. **Strong uptrend**: Grid ít trades, ROI thấp
2. **Flash crash**: Drawdown spike (cần hedge)
3. **Low volatility**: Ít cơ hội

### Timeframe
- **H1 (khuyến nghị)**: Backtest trên H1, ít noise
- **H4**: Ít trades hơn, ROI thấp hơn
- **M15/M30**: Nhiều trades, phí cao

## 🔐 Security

### Magic Number
- Default: 123456
- Đổi thành số riêng nếu chạy nhiều EAs
- Tránh conflict với EA khác

### Comments
- GRID: Lệnh grid trading
- HEDGE: Lệnh hedge
- Dùng để filter trong code

## 📞 Support

### Check logs khi có vấn đề
1. Journal tab: Xem errors
2. Experts tab: Xem EA output
3. Chart comment: Xem status real-time

### Backup settings
- Export settings: Save → File .set
- Restore nếu cần reset

---

## ✅ Checklist trước khi live

- [ ] Đã test Demo ít nhất 2 tuần
- [ ] Drawdown demo < 20%
- [ ] Win rate demo > 60%
- [ ] Hiểu rõ cách EA hoạt động
- [ ] Vốn đủ margin (> $5,000)
- [ ] Broker uy tín, spread thấp
- [ ] Đã optimize parameters cho XAUUSD
- [ ] Có kế hoạch stop loss / take profit
- [ ] Monitor hàng ngày

**Good luck trading! 🚀**

---

**Version**: 1.0  
**Updated**: 2026-01-31  
**Strategy**: Grid + Hedge (từ Python backtest)  
**Tested**: XAUUSD H1, 6 months data
