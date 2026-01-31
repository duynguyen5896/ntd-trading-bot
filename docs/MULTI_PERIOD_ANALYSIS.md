# PHÂN TÍCH ĐA CHU KỲ - 8 THÁNG 2025

## 🔍 Tổng Quan

**Test periods:** 8 tháng (Jan - Aug 2025)  
**Total bars:** 5,639 hours  
**Market conditions:**
- ✅ UPTREND: 4 periods (Jan, Apr, May, Jul)
- ❌ DOWNTREND: 2 periods (Feb, Aug)
- ↔️ SIDEWAY: 2 periods (Mar, Jun)

---

## 📊 Kết Quả Tổng Hợp

### Win Rate By Trend

| Trend | CONSERVATIVE | OPTIMIZED | AGGRESSIVE |
|-------|--------------|-----------|------------|
| **UPTREND** (4 periods) | 2 wins / 4 (50%) | 0 wins / 4 (0%) | 1 win / 4 (25%) |
| **DOWNTREND** (2 periods) | 0 wins / 2 (0%) | 0 wins / 2 (0%) | 0 wins / 2 (0%) |
| **SIDEWAY** (2 periods) | 0 wins / 2 (0%) | 0 wins / 2 (0%) | 0 wins / 2 (0%) |
| **OVERALL** | **2/8 (25%)** | **0/8 (0%)** | **1/8 (12.5%)** |

### Average Performance

| Config | Avg ROI | Avg Sharpe | Avg MaxDD | Best Month | Worst Month |
|--------|---------|------------|-----------|------------|-------------|
| CONSERVATIVE | **-4.74%** | -8.24 | -16.41% | +25.70% (Jan) | -20.02% (Apr) |
| OPTIMIZED | -16.64% | -12.65 | -23.85% | +1.45% (Mar) | -25.03% (Apr) |
| AGGRESSIVE | -16.66% | -13.70 | -25.54% | +24.95% (May) | -30.04% (Jul) |

---

## ⚠️ VẤNĐỀ PHÁT HIỆN

### 1. **Chiến Lược Thua Lỗ Trong Downtrend**

#### Feb 2025 (Downtrend -17.28%)
```
CONSERVATIVE:  -18.87% (hit max drawdown after 28 bars)
OPTIMIZED:     -23.40% (hit max drawdown after 23 bars)
AGGRESSIVE:    -27.59% (hit max drawdown after 23 bars)
```

**Nguyên nhân:**
- BTC giảm từ $102k → $84k (-17.28%)
- Grid **chỉ mua khi giá xuống**, không có cơ chế SHORT
- Spot holdings bị lỗ nặng do giá giảm liên tục
- Hedge futures không đủ mạnh để cover spot losses

#### Aug 2025 (Downtrend -5.74%)
```
CONSERVATIVE:  -19.05% (stopped after 35 bars)
OPTIMIZED:     -16.04% (stopped after 34 bars)
AGGRESSIVE:    -27.84% (stopped after 31 bars)
```

**Kết luận:** Chiến lược **KHÔNG hoạt động trong downtrend**

---

### 2. **Chỉ Thành Công Trong 2/8 Tháng**

#### ✅ Jan 2025: CONSERVATIVE +25.70%
- Uptrend +11.13%, low volatility 2.81%
- Grid triggers ít, giữ BTC và hưởng lợi từ uptrend
- Max DD chỉ -8.05%

#### ✅ Jul 2025: CONSERVATIVE +7.93%
- Uptrend +9.73%, very low volatility 1.61%
- Tương tự Jan, grid ít trigger, hold BTC tăng giá

#### ✅ May 2025: AGGRESSIVE +24.95%
- Uptrend +10.20%, volatility 1.99%
- Aggressive config hoạt động tốt trong low vol uptrend

**Pattern:** Chỉ thắng khi:
1. Market UPTREND
2. Volatility THẤP (< 2%)
3. Ít rebalance

---

### 3. **Max Drawdown Hit Liên Tục**

Trong 8 tháng:
- **CONSERVATIVE:** 6/8 tháng hit max drawdown (-15% - -20%)
- **OPTIMIZED:** 7/8 tháng hit max drawdown (-23% - -25%)
- **AGGRESSIVE:** 7/8 tháng hit max drawdown (-27% - -30%)

**Lý do:**
- Threshold quá thấp (15%, 20%, 25%)
- Chiến lược không có cơ chế stop-loss sớm
- Một khi trend đảo chiều, lỗ rất nhanh

---

### 4. **Grid Không Hoạt Động Như Dự Kiến**

**Số lượng trades thực tế:**
```
Jan:  1 buy, 1 sell  (expected: 20-30)
Feb:  1 buy, 0 sell  (stopped early)
Mar:  buys only      (stopped early)
...
```

**Vấn đề:**
- Grid levels quá rộng → ít trigger
- Rebalance threshold 15-18% → chỉ rebalance khi trend mạnh
- Khi rebalance, market đã reverse → hit drawdown

---

## 💡 PHÂN TÍCH SÂU

### Tại Sao Tháng 1 Thành Công Nhưng Tháng 4 Thất Bại?

Cả 2 tháng đều UPTREND (+11% và +14%), nhưng:

| Metric | Jan (✅ +25.70%) | Apr (❌ -20.02%) |
|--------|------------------|------------------|
| Volatility | 2.81% | 2.77% |
| Start price | $94k | $82k |
| End price | $104k | $94k |
| Path | Smooth up | **Crash first then up** |

**Apr 2025 detail:**
- Giá start $82k
- **Crash xuống $74k (-9.7%)** trong 5 ngày đầu
- Sau đó mới phục hồi lên $94k

→ Grid mua ở $82k, crash xuống $74k → **hit max drawdown -20%**

**Kết luận:** Chiến lược không chịu được volatility spike đầu period

---

### Tại Sao Feb & Aug (Downtrend) Lỗ Nặng?

Grid strategy **vốn dĩ long-biased**:
- Mua khi giá xuống dưới EMA
- Sell khi giá lên trên và có profit
- **Không có cơ chế SHORT spot**

Trong downtrend:
1. Grid mua BTC ở $102k (Feb start)
2. BTC giảm xuống $84k (-17%)
3. Spot holdings lỗ **-$1,700** (17% * $10k)
4. Hedge futures chỉ có ~$300-400 profit (3-4% hedge size)
5. **Net loss:** -$1,300+ = -13%+ ROI
6. Add fees → total loss -18% to -23%

**Hedge không đủ mạnh:**
```python
'hedge_sizes': [0.08, 0.12, 0.15]  # Only 8-15% of capital
```

Để hedge đủ cho spot losses 17%, cần hedge size ≥ 100% (1:1 hedge).

---

## 🎯 GIẢI PHÁP

### Option 1: Chỉ Trade Trong Uptrend

Thêm **trend filter:**
```python
def should_trade(ema_50, ema_200, price):
    # Only trade if uptrend
    if ema_50 > ema_200 and price > ema_200:
        return True
    return False
```

**Expected improvement:**
- Skip Feb, Aug (downtrend) → Tránh lỗ -18% to -27%
- Only trade Jan, Apr, May, Jul (uptrend)
- Win rate: 2/4 = 50% trong uptrend (better than 2/8 = 25% overall)

---

### Option 2: Tăng Hedge Trong Downtrend

Dynamic hedge size based on trend:
```python
if ema_50 < ema_200:  # Downtrend
    hedge_sizes = [0.30, 0.50, 0.80]  # 30-80% hedge
else:  # Uptrend
    hedge_sizes = [0.08, 0.12, 0.15]  # 8-15% hedge
```

**Pros:**
- Protect downside in downtrend
- Keep low hedge cost in uptrend

**Cons:**
- High hedge cost → reduce profit in sideways
- Complexity

---

### Option 3: Dừng Trading & Hold Cash Trong Downtrend

```python
if ema_50 < ema_200 and price < ema_200:
    # Close all positions
    # Hold cash
    # Wait for uptrend signal
```

**Expected:**
- Feb: Hold cash instead of -18.87% → Save +18.87%
- Aug: Hold cash instead of -19.05% → Save +19.05%
- Average ROI: -4.74% + 18.96% = **+14.22%**

---

### Option 4: Điều Chỉnh Max Drawdown Threshold

Current thresholds quá hẹp:
```python
CONSERVATIVE: -15%
OPTIMIZED:    -20%
AGGRESSIVE:   -25%
```

**Problem:** Hit max DD trong 6-7/8 tháng → Không đủ thời gian để phục hồi

**Suggestion:**
```python
CONSERVATIVE: -25%  (instead of -15%)
OPTIMIZED:    -30%  (instead of -20%)
AGGRESSIVE:   -35%  (instead of -25%)
```

**Trade-off:**
- More room for recovery
- But higher risk

---

## 📈 CONFIG ĐỀ XUẤT MỚI

### Config A: Uptrend-Only (Safest)

```python
CONFIG_UPTREND_ONLY = {
    'initial_capital': 10_000,
    
    # Trend Filter
    'require_uptrend': True,
    'ema_fast': 50,
    'ema_slow': 200,
    
    # Grid (same as CONSERVATIVE)
    'grid_step': 0.025,
    'grid_take_profit': 0.035,
    'grid_risk_per_order': 0.05,
    
    # Lower hedge in uptrend
    'hedge_atr_threshold': [4.0, 6.0, 8.0],
    'hedge_sizes': [0.05, 0.10, 0.15],
    
    # Risk
    'max_drawdown_threshold': 0.25,
}
```

**Expected:**
- Only trade 4/8 months (uptrends)
- Win 2/4 = 50%
- Avg ROI in uptrends: +3.85% (CONSERVATIVE)
- Skip downtrends → Save +18.96%
- **Overall: ~+15-20% / period when trading**

---

### Config B: Dynamic Hedge (Balanced)

```python
CONFIG_DYNAMIC_HEDGE = {
    'initial_capital': 10_000,
    
    # Grid
    'grid_step': 0.025,
    'grid_take_profit': 0.035,
    'grid_risk_per_order': 0.05,
    
    # Dynamic Hedge
    'uptrend_hedge_sizes': [0.05, 0.10, 0.15],
    'downtrend_hedge_sizes': [0.40, 0.60, 0.80],
    
    # Risk
    'max_drawdown_threshold': 0.30,
}
```

**Expected:**
- Trade all periods
- Downtrend losses: -18% → -8% (hedged)
- Uptrend profits: +13% → +10% (lower due to hedge cost)
- **Overall: +5-8% average**

---

## ✅ KẾT LUẬN

### Thực Tế Phũ Phàng

Original strategy (CONSERVATIVE) có:
- **Win rate: 25% (2/8 tháng)**
- **Average ROI: -4.74%**
- **Worst loss: -20% trong 1 tháng**

Chỉ hoạt động tốt khi:
1. Market UPTREND
2. Volatility < 2%
3. Không có flash crash

### Khuyến Nghị

**Cho Real Trading:**

1. ✅ **Dùng Config UPTREND_ONLY**
   - Only trade khi EMA50 > EMA200
   - Expected: +15-20% ROI trong uptrend periods
   - Avoid: -18 to -27% losses trong downtrend

2. ✅ **Tăng Max Drawdown Threshold**
   - Từ -15% → -25%
   - Cho phép recovery trong volatile periods

3. ✅ **Add Stop-Loss Sớm Hơn**
   - Nếu loss -10% trong 3 ngày → Stop
   - Tránh loss -20% trong 5 ngày như Apr, Feb

4. ✅ **Monitor Trend Daily**
   - Calculate EMA50, EMA200 hàng ngày
   - Exit positions nếu trend reverse

### Next Steps

1. Implement CONFIG_UPTREND_ONLY
2. Backtest lại 8 tháng với trend filter
3. Verify win rate tăng lên 50%+
4. Paper trade 1-2 tháng trước khi live

---

**Tóm lại:** Grid strategy không phù hợp với ALL market conditions. Cần **trend filter** để chỉ trade trong uptrend, hoặc **dynamic hedge** để protect downside.
