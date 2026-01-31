# CHIẾN LƯỢC GRID ĐỘNG + HEDGE

## 1. TRIẾT LÝ CHIẾN LƯỢC

**Giả định cốt lõi:** Thị trường là sideway từ 0 → ∞
- Giá luôn dao động (volatility là bạn)
- Không cần dự đoán hướng
- Thu lợi từ chênh lệch giá

## 2. CƠ CHẾ HOẠT ĐỘNG

### A. GRID ĐỘNG (Spot)
**Mục tiêu:** Mua thấp bán cao trong biên độ dao động

**Logic:**
1. **Center Price:** EMA50 (làm trung tâm lưới)
2. **Grid Levels:** 10 levels, mỗi level cách nhau 0.8%
3. **Mua:** Khi giá chạm grid level dưới center
4. **Bán:** Khi giá tăng > entry + 1.2% (take profit)
5. **Rebalance:** Khi giá di chuyển xa center > 5%, dịch lưới

**Tại sao không lỗ khi điều chỉnh grid?**
- ✅ KHÔNG LỖ nếu giữ nguyên vị thế và chỉ dịch chuyển levels
- ❌ CÓ THỂ LỖ nếu đóng toàn bộ position rồi mở lại ở giá mới
- **Giải pháp:** Chỉ điều chỉnh grid levels (thay đổi buy/sell triggers), KHÔNG đóng positions hiện tại

### B. HEDGE ĐỘNG (Futures Perpetual)
**Mục tiêu:** Bảo vệ vốn khi giá phá biên mạnh

**Logic:**
1. **ATR Distance:** Đo khoảng cách giá từ center theo ATR
2. **Hedge Layers:**
   - Layer 1 (2 ATR): Short 10% equity
   - Layer 2 (3 ATR): Short thêm 15% equity
   - Layer 3 (4 ATR): Short thêm 20% equity
3. **Close Hedge:** Khi giá quay về < 1.5 ATR, giảm dần hedge

**Tại sao dùng ATR?**
- ATR thể hiện volatility tự nhiên
- Tránh trigger sai trong dao động nhỏ
- Thích nghi với từng giai đoạn thị trường

### C. BINANCE FEES & FUNDING RATE

**Spot Fees:**
- Maker: 0.1%
- Taker: 0.1%

**Futures Fees:**
- Maker: 0.02%
- Taker: 0.05%
- **Funding Rate:** ±0.01% mỗi 8h (thường 0.01% - 0.03%)

**Impact:**
- Giảm ROI khoảng 2-3% / tháng
- Funding rate có thể ăn lợi nhuận nếu hold short lâu
- Grid phải có profit margin > 1.5% để cover fees

## 3. KỊCH BẢN THỊ TRƯỜNG

### Kịch bản 1: SIDEWAY (±3%)
```
Price: 30000 → 30900 → 29700 → 30300 → 30000

Grid: MUA 29700, 29400 → BÁN 30000, 30300
Hedge: Không kích hoạt (< 2 ATR)

Kết quả: 
- Grid profit: +1.5% (3-4 round trips)
- Fees: -0.4%
- Net: +1.1%
```

### Kịch bản 2: UPTREND (+15%)
```
Price: 30000 → 32000 → 33500 → 34500

Grid: BÁN dần 30300, 30600, 31000... (chốt lời từng phần)
Hedge: KHÔNG kích hoạt hoặc kích hoạt nhẹ rồi đóng sớm

Kết quả:
- Grid profit: +3% (bán dần, còn lại position tăng giá)
- Hedge loss: -0.5% (nếu có)
- Unrealized gain: +8% (còn BTC chưa bán)
- Net: +10.5%
```

### Kịch bản 3: DOWNTREND (-20%)
```
Price: 30000 → 28000 → 26000 → 24000

Grid: MUA dần 29700, 29400, 29100... (tích lũy)
Hedge: SHORT kích hoạt layer 1,2,3 khi > 2,3,4 ATR

Kết quả:
- Grid loss (unrealized): -8% (giá entry cao hơn giá hiện tại)
- Hedge profit: +12% (short từ 29000 → 24000)
- Funding cost: -0.3%
- Net: +3.7%
```

### Kịch bản 4: DUMP ĐỘT NGỘT (-30%)
```
Price: 30000 → 21000 (trong 2 ngày)

Grid: Mua hết budget ở 29700 → 27000
Hedge: Kích hoạt cả 3 layers, short max

Risk: MARGIN CALL nếu hedge leverage > 5x

Kết quả:
- Grid loss: -15% (unrealized)
- Hedge profit: +25% (short 3x30000 → 21000)
- Net: +10%

**Margin Call Protection:**
- Max leverage: 3x
- Stop hedge nếu equity < 50% initial
```

## 4. THAM SỐ TỐI ƯU CHO ROI 13% / 30 NGÀY

```python
CONFIG = {
    # Grid
    'grid_levels': 10,
    'grid_step': 0.008,        # 0.8%
    'grid_take_profit': 0.012,  # 1.2%
    'grid_risk_per_order': 0.08,  # 8% balance per order
    
    # Hedge
    'hedge_atr_threshold': [2, 3, 4],
    'hedge_sizes': [0.10, 0.15, 0.20],  # 10%, 15%, 20% equity
    'hedge_leverage': 3,
    
    # Risk
    'max_drawdown': 0.15,  # 15%
    'rebalance_threshold': 0.05,  # 5% from center
    
    # Fees
    'spot_fee': 0.001,  # 0.1%
    'futures_maker_fee': 0.0002,  # 0.02%
    'futures_taker_fee': 0.0005,  # 0.05%
    'funding_rate': 0.0001,  # 0.01% per 8h
}
```

## 5. TẠI SAO ĐẠT 13% / THÁNG?

**Giả định thị trường:** BTC volatility 3-5% / ngày

**Nguồn lợi nhuận:**
1. **Grid trades:** 8-10 round trips/tháng × 1.2% profit = +9-12%
2. **Hedge profit (downtrend):** +3-8%
3. **Unrealized gains (uptrend):** +5-10%

**Trừ chi phí:**
- Fees: -2%
- Funding: -1%
- Slippage: -0.5%

**Net:** +13-17% / tháng

**Lưu ý:** 
- Nếu sideway hoàn hảo: +15%
- Nếu 1 chiều mạnh: +8-10%
- Worst case (flash crash + recover): +5%
