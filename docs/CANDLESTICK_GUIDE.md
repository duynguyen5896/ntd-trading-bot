# Hướng dẫn sử dụng Candlestick Charts

## Quick Start - 3 bước

### Bước 1: Chạy backtest
```bash
python main.py
```

### Bước 2: Chọn test mode
```
Select test mode:
1. Real BTC Data          ← Test với dữ liệu thực từ Yahoo Finance
2. Simulated Crash Data   ← Test kịch bản crash $60k → $13k
3. Load Custom CSV        ← Upload file CSV của bạn
4. Compare All Configs    ← So sánh tất cả configs
```

### Bước 3: Tạo charts
```
Generate performance charts? (y/n): y

[CHART] Performance charts saved to: backtest_results_v2.png
[CHART] Candlestick with entry points saved to: entry_points_ohlc.png
```

## Ví dụ thực tế

### Test Crash Scenario ($60k → $50k)

**Input:**
```bash
python main.py
→ Chọn: 2 (Simulated Crash Data)
→ Chọn: 1 (Gradual crash 180 days)
→ Chọn: 1 (Single config test)
→ Chọn: 1 (adaptive)
→ Generate charts? y
```

**Output:**
```
Running backtest on 720 bars...
Period: 2022-01-01 00:00:00 to 2022-01-30 23:00:00

Results:
   ROI: +413.75%
   Grid Trades: 14 buys, 13 sells
   Hedge Trades: 28 opens, 25 closes

Generating charts...
[CHART] Performance charts saved to: backtest_results_v2.png
[CHART] Candlestick with entry points saved to: entry_points_ohlc.png
```

**Candlestick Chart sẽ có:**
- 14 mũi tên xanh ▲ (Grid BUY)
- 13 mũi tên đỏ ▼ (Grid SELL)
- 28 hình vuông cam ■ (Hedge OPEN)
- 25 kim cương xanh ◆ (Hedge CLOSE)
- Đường EMA50 màu tím

### Test Real Data (Jan 2025)

**Input:**
```bash
python main.py
→ Chọn: 1 (Real BTC Data)
→ Start date: 2025-01-01
→ End date: 2025-01-31
→ Chọn: 1 (Single config test)
→ Chọn: 3 (conservative)
→ Generate charts? y
```

**Output:**
```
Downloaded 730 bars

Results:
   ROI: +25.70%
   Grid Trades: 8 buys, 8 sells
   Hedge Trades: 3 opens, 3 closes

[CHART] Candlestick with entry points saved to: entry_points_ohlc.png
```

## Đọc hiểu Candlestick Chart

### Chart 1: Grid Trading Entries/Exits

```
Price Chart:
┌─────────────────────────────────────────┐
│ $58,000                               ▼ │ ← Grid SELL (chốt lời)
│                                  ┌───┐  │
│ $57,000    ────────────EMA50─────┤   │  │ ← EMA50 (trung tâm)
│                          ┌───┐   │   │  │
│ $56,000                  │   │   └───┘  │
│                    ┌───┐ │   │          │
│ $55,000            │   │ └───┘        ▲ │ ← Grid BUY (mua vào)
│              ┌───┐ │   │                │
│ $54,000      │   │ └───┘                │
└─────────────────────────────────────────┘
   Jan 10   Jan 15   Jan 20   Jan 25
```

**Giải thích:**
- Giá giảm xuống $55k (dưới EMA $56k) → **Mũi tên xanh ▲** (Grid BUY)
- Giá tăng lên $58k (trên EMA $57k) → **Mũi tên đỏ ▼** (Grid SELL)
- Chênh lệch: $3k profit (+5.4%)

### Chart 2: Hedge Entries/Exits

```
Price Chart:
┌─────────────────────────────────────────┐
│ $62,000                             ■   │ ← Hedge OPEN (giá xa EMA)
│                                ┌────┐   │
│ $60,000    ─────EMA50──────────┤    │   │
│                          ┌────┐│    │   │
│ $58,000                  │    ││    │◆  │ ← Hedge CLOSE (giá về gần EMA)
│              ┌────┐      │    ││    │   │
│ $56,000      │    │      │    │└────┘   │
└─────────────────────────────────────────┘
```

**Giải thích:**
- Giá $62k, EMA $60k, khoảng cách >2.5 ATR → **Hình vuông cam ■** (Hedge OPEN)
- Giá giảm về $58k gần EMA → **Kim cương xanh ◆** (Hedge CLOSE)
- Hedge profit: Short từ $62k → cover $58k = $4k/BTC

## Phân tích Patterns

### Pattern 1: Grid hoạt động hiệu quả ✅

**Đặc điểm:**
- Mũi tên xanh ▲ xuất hiện ở **đáy nến**
- Mũi tên đỏ ▼ xuất hiện ở **đỉnh nến**
- Khoảng cách đều (1.6% grid step)
- Entries xung quanh EMA50

**Ví dụ:**
```
$57k ▼ SELL     ← Bán đỉnh
$56.5k (EMA)
$56k ▲ BUY      ← Mua đáy
$55k ▲ BUY      
```

### Pattern 2: Grid chưa tối ưu ⚠️

**Đặc điểm:**
- Nhiều mũi tên xanh ▲ liên tiếp (mua nhiều lần)
- Ít mũi tên đỏ ▼ (không bán được)
- Entries xa EMA50

**Ví dụ:**
```
$60k
$58k ▲ BUY      
$56k ▲ BUY      ← Mua liên tục
$54k ▲ BUY      
$52k ▲ BUY      ← Grid step quá nhỏ!
```

**Giải pháp:** Tăng grid_step từ 1.2% → 1.6%

### Pattern 3: Hedge bảo vệ tốt ✅

**Đặc điểm:**
- Số lượng ■ OPEN ≈ ◆ CLOSE
- Hedge kích hoạt khi price spike
- Đóng hedge khi price normalize

**Ví dụ:**
```
$65k ■          ← Open hedge (bảo vệ)
$63k            
$61k ◆          ← Close hedge (chốt profit)
```

## So sánh Configs qua Charts

### SCALPING vs ADAPTIVE

**SCALPING (1.2% step):**
- Nhiều markers (60+ entries)
- Entries dày đặc
- Phù hợp high volatility

**ADAPTIVE (1.6% step):**
- Ít markers hơn (30-40 entries)
- Entries cân bằng
- Win rate cao hơn

**Chart comparison:**
```
SCALPING:              ADAPTIVE:
▼▼▼                    ▼  
 ▲▲▲▲                   ▲  
  ▼▼                     ▼ 
   ▲▲▲                    ▲
```

## Tips & Tricks

### 1. Zoom vào thời điểm quan trọng
- Mở file PNG trong image viewer
- Zoom vào khu vực có nhiều markers
- Phân tích từng entry/exit

### 2. So sánh multiple periods
```bash
# Test Jan 2025
python main.py → Jan data → Save as entry_jan.png

# Test Feb 2025
python main.py → Feb data → Save as entry_feb.png

# Compare side by side
```

### 3. Identify best entry timing
- Grid BUY ▲ tại đáy nến → Good timing ✅
- Grid BUY ▲ tại đỉnh nến → Bad timing ❌
- Nhiều BUY đáy → Config tốt
- Nhiều BUY đỉnh → Cần điều chỉnh

### 4. Validate hedge effectiveness
- Count ■ OPEN vs ◆ CLOSE
- Nếu OPEN >> CLOSE → Hedge không đóng (risk!)
- Nếu OPEN ≈ CLOSE → Hedge balanced ✅

## Troubleshooting

### Q: Chart không có markers?
**A:** Không có trades được thực hiện
- Kiểm tra grid_step (có thể quá rộng)
- Thử ADAPTIVE hoặc SCALPING config
- Tăng backtest period

### Q: Markers chồng lên nhau?
**A:** Quá nhiều entries
- Tăng grid_step
- Giảm max_grid_levels
- Zoom vào để xem rõ hơn

### Q: Nến không rõ?
**A:** File resolution thấp
- Mở file PNG gốc (không xem preview)
- DPI: 150 (high quality)
- Zoom trong image viewer

### Q: Làm sao lưu charts?
**A:** Copy files ra thư mục khác
```bash
# Windows
Copy-Item entry_points_ohlc.png results\crash_adaptive.png

# Rename để phân biệt
mv entry_points_ohlc.png entry_crash_30days.png
```

## Advanced Usage

### Custom markers cho analysis riêng

Edit `core/performance.py`:

```python
# Đánh dấu điểm đặc biệt
special_buys = trades[trades['profit'] > 500]  # Lệnh lời >$500
ax1.scatter(special_buys['timestamp'], special_buys['price'],
           color='gold', marker='★', s=300, label='Big Wins')

# Highlight loss trades
loss_sells = trades[trades['profit'] < 0]
ax1.scatter(loss_sells['timestamp'], loss_sells['price'],
           color='black', marker='x', s=200, label='Losses')
```

### Export data để phân tích thêm

```python
# Sau khi run backtest
trades = results['trades']
trades.to_csv('trades_with_markers.csv')

# Phân tích trong Excel:
# - Filter Grid BUY với profit > $100
# - Tìm pattern time of day
# - Calculate avg profit per entry
```

## Summary

**Candlestick Charts giúp bạn:**
1. ✅ Visualize chiến lược trên giá thực
2. ✅ Hiểu tại sao ROI cao/thấp
3. ✅ Tìm timing tốt nhất để entry
4. ✅ Validate hedge effectiveness
5. ✅ Compare configs trực quan
6. ✅ Debug strategy issues
7. ✅ Optimize parameters

**2 files quan trọng:**
- `backtest_results_v2.png` - Performance metrics
- `entry_points_ohlc.png` - **Visual strategy analysis** ⭐

---

**Xem thêm:** [CANDLESTICK_CHARTS.md](CANDLESTICK_CHARTS.md) - Tài liệu chi tiết
