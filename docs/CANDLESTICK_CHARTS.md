# Candlestick Charts với Entry/Exit Points

## Tổng quan

Hệ thống backtest hiện có thể tạo candlestick chart (biểu đồ nến) OHLC với các điểm mở/đóng vị thế được đánh dấu rõ ràng.

## Loại biểu đồ

### 1. Performance Overview (backtest_results_v2.png)
Biểu đồ tổng quan với 6 charts:
- Equity Curve (đường vốn)
- Price & EMA (giá & trung tâm grid)
- Spot Position & Cash
- Futures Short Position
- Unrealized PnL
- Cumulative Costs

### 2. **CANDLESTICK với Entry Points (entry_points_ohlc.png) - MỚI!**
2 biểu đồ nến OHLC:

#### Chart 1: Grid Trading Entries/Exits
- **Nến xanh/đỏ**: Giá OHLC (Open, High, Low, Close)
- **Mũi tên xanh ↑**: Điểm Grid BUY (mua spot)
- **Mũi tên đỏ ↓**: Điểm Grid SELL (bán spot, chốt lời)
- **Đường tím đứt**: EMA50 (trung tâm grid)

#### Chart 2: Hedge Entries/Exits
- **Nến xanh/đỏ**: Giá OHLC
- **Hình vuông cam**: Điểm mở Hedge (short futures)
- **Hình kim cương xanh**: Điểm đóng Hedge (close futures)
- **Đường tím đứt**: EMA50

## Ý nghĩa các marker

| Marker | Màu | Ý nghĩa | Hành động |
|--------|-----|---------|-----------|
| ▲ (Triangle up) | Xanh lá | Grid BUY | Mua BTC spot khi giá < EMA50 |
| ▼ (Triangle down) | Đỏ | Grid SELL | Bán BTC spot khi giá > EMA50 |
| ■ (Square) | Cam | Hedge OPEN | Mở short futures (bảo hiểm) |
| ◆ (Diamond) | Xanh dương | Hedge CLOSE | Đóng short futures |

## Cách đọc biểu đồ

### Ví dụ Grid Trading
```
Price: $55,000
EMA50: $56,000 (đường tím)

[Nến đỏ giảm]
     ↑ ← Grid BUY tại $54,800 (giá < EMA)
[Nến xanh]
[Nến xanh tăng]
     ↓ ← Grid SELL tại $56,200 (giá > EMA, chốt lời)
```

### Ví dụ Hedge
```
Price tăng mạnh xa EMA:
     ■ ← Mở hedge short (bảo vệ lợi nhuận)

Price quay về gần EMA:
     ◆ ← Đóng hedge (giảm rủi ro)
```

## Đặc điểm kỹ thuật

### OHLC Candlestick
- **Nến xanh**: Close > Open (giá tăng)
- **Nến đỏ**: Close < Open (giá giảm)
- **Que dọc**: Khoảng High-Low
- **Thân nến**: Khoảng Open-Close

### Marker Details
- **Kích thước**: 150 pixels
- **Độ trong suốt**: 80% (alpha=0.8)
- **Viền**: 1.5px màu đậm
- **Z-order**: 5 (luôn hiện trên nến)

## Khi nào sử dụng

### Phân tích Grid Trading
- Xem chiến lược mua/bán tại mức giá nào
- Kiểm tra grid có tuân theo EMA50 không
- Đánh giá spacing giữa các lệnh buy/sell
- Tìm pattern thắng/thua

### Phân tích Hedge
- Xem khi nào hedge được kích hoạt
- Kiểm tra ATR distance trigger
- Đánh giá timing đóng hedge
- Tính toán hedge effectiveness

### So sánh configs
- Grid step 1.6% vs 2.5%: So sánh số lượng entries
- Conservative vs Aggressive: So sánh risk exposure
- With/Without hedge: So sánh downside protection

## Cách tạo chart

### Từ main.py
```bash
python main.py
# Chọn test mode (1-4)
# Khi hỏi "Generate performance charts? (y/n):"
# → Nhập: y
```

### Từ code
```python
from core.performance import PerformanceAnalyzer

analyzer = PerformanceAnalyzer(results, config)
analyzer.plot_results()
# Tạo 2 files:
# - backtest_results_v2.png
# - entry_points_ohlc.png
```

### Test riêng
```bash
python test_candlestick.py
# Chạy test nhanh với crash scenario
```

## Ví dụ kết quả

### Crash Scenario ($60k → $50k)
```
ROI: +413.75%
Grid Trades: 14 buys, 13 sells
Hedge Trades: 28 opens, 25 closes

File: entry_points_ohlc.png (345 KB)
- Chart 1: 14 mũi tên xanh, 13 mũi tên đỏ
- Chart 2: 28 hình vuông cam, 25 kim cương xanh
```

### Sideway Market
```
ROI: +71.93%
Grid Trades: 45 buys, 44 sells
Hedge Trades: 2 opens, 2 closes

File: entry_points_ohlc.png
- Chart 1: Nhiều entries quanh EMA50
- Chart 2: Ít hedge (chỉ khi price spike)
```

## Phân tích patterns

### Pattern 1: Grid hoạt động tốt
- Mũi tên xanh ↑ gần đáy nến
- Mũi tên đỏ ↓ gần đỉnh nến
- Khoảng cách đều giữa các entry
- Luôn xung quanh EMA50

### Pattern 2: Hedge hiệu quả
- Hình vuông cam ■ khi price xa EMA
- Kim cương xanh ◆ khi price về gần EMA
- Số lượng open ≈ close (cân bằng)

### Pattern 3: Cần cải thiện
- Nhiều mũi tên xanh ↑ liên tiếp (mua nhiều)
- Ít mũi tên đỏ ↓ (không bán được)
- → Grid step quá rộng
- Hedge open nhiều nhưng không close
- → ATR trigger chưa tối ưu

## Customization

### Thay đổi marker
Edit `core/performance.py`, method `_plot_candlestick_with_entries`:

```python
# Grid buys - thay marker và màu
ax1.scatter(..., marker='^', color='green')
# Marker options: '^', 'v', 'o', 's', 'D', '*', 'P', 'X'

# Thay size
ax1.scatter(..., s=200)  # Lớn hơn (default: 150)

# Thay độ trong suốt
ax1.scatter(..., alpha=0.9)  # Đậm hơn (default: 0.8)
```

### Thêm indicators
```python
# Thêm vào _plot_candlestick_with_entries:

# Bollinger Bands
ax1.fill_between(df['timestamp'], upper_band, lower_band, 
                 alpha=0.1, color='gray')

# Support/Resistance
ax1.axhline(y=support_level, color='green', 
           linestyle=':', linewidth=2)
```

## Troubleshooting

### Chart trống
**Vấn đề**: Không có marker trên chart

**Nguyên nhân**: Không có trades được thực hiện

**Giải pháp**: 
- Kiểm tra config grid_step (có thể quá rộng)
- Kiểm tra dữ liệu có đủ volatility không
- Thử config ADAPTIVE hoặc SCALPING

### Nến không hiện
**Vấn đề**: Chỉ thấy marker, không thấy nến

**Nguyên nhân**: Data không có OHLC

**Giải pháp**:
- Yahoo Finance data tự động có OHLC
- generate_crash_data() tự động tạo OHLC
- CSV file cần có columns: open, high, low, close

### Marker chồng lên nhau
**Vấn đề**: Quá nhiều entries cùng lúc

**Nguyên nhân**: Grid step quá nhỏ hoặc volatility cao

**Giải pháp**:
- Tăng grid_step (1.2% → 1.6% → 2.5%)
- Giảm max_grid_levels
- Zoom vào thời gian cụ thể

## Performance

### File sizes
- Crash 30 days (720 bars): ~350 KB
- Real 1 month (730 bars): ~380 KB
- Real 8 months (5800 bars): ~1.2 MB

### Generation time
- 720 bars: ~2-3 seconds
- 5800 bars: ~8-12 seconds

### Resolution
- DPI: 150 (high quality)
- Width: 20 inches
- Height: 14 inches
- Format: PNG

## Best Practices

1. **Luôn tạo chart sau mỗi backtest**
   - Giúp hiểu tại sao ROI cao/thấp
   - Phát hiện bugs trong strategy

2. **So sánh multiple scenarios**
   - Uptrend vs Downtrend vs Sideway
   - Xem pattern entries khác nhau như thế nào

3. **Zoom vào thời điểm quan trọng**
   - Khi ROI thay đổi đột ngột
   - Khi drawdown lớn
   - Khi hedge được kích hoạt

4. **Lưu charts cho từng config**
   - Đổi tên file: `entry_points_adaptive.png`
   - So sánh side-by-side
   - Chọn config tốt nhất

## Changelog

### Version 2.0 (Current)
- ✅ Candlestick OHLC charts
- ✅ Grid buy/sell markers
- ✅ Hedge open/close markers
- ✅ EMA50 overlay
- ✅ 2-chart layout (Grid + Hedge riêng biệt)
- ✅ OHLC data trong backtest engine
- ✅ Test script: test_candlestick.py

### Version 1.0 (Previous)
- Performance overview (6 charts)
- Equity curve
- Price & EMA line chart
- Position tracking
- Cost analysis

---

**Tạo bởi**: Restructuring Update 2.0  
**Ngày**: 2026-01-31  
**File**: `entry_points_ohlc.png` - Candlestick với Entry/Exit Points
