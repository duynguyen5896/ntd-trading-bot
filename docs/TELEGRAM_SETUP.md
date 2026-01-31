# Hướng dẫn tạo Telegram Bot và lấy Chat ID

## 🤖 Bước 1: Tạo Telegram Bot

1. **Mở Telegram app**

2. **Tìm @BotFather**
   - Search: `@BotFather`
   - Hoặc: https://t.me/BotFather

3. **Tạo bot mới**
   ```
   /start
   /newbot
   ```

4. **Đặt tên cho bot**
   ```
   Name: My Trading Bot
   Username: my_trading_bot (phải kết thúc bằng "bot")
   ```

5. **Copy Bot Token**
   ```
   BotFather sẽ trả về:
   Use this token to access the HTTP API:
   123456789:ABCdefGHIjklMNOpqrsTUVwxyz
   
   → Copy token này
   ```

## 💬 Bước 2: Lấy Chat ID

### Option A: Dùng @userinfobot (Dễ nhất)

1. **Tìm @userinfobot**
   - Search: `@userinfobot`
   - Hoặc: https://t.me/userinfobot

2. **Start bot**
   ```
   /start
   ```

3. **Copy Chat ID**
   ```
   Bot sẽ trả về:
   Id: 123456789
   
   → Copy số này
   ```

### Option B: Dùng API (Nếu Option A không work)

1. **Nhắn tin cho bot của bạn**
   - Tìm bot vừa tạo: @my_trading_bot
   - Gửi bất kỳ tin nhắn: `/start` hoặc `hello`

2. **Vào browser, mở URL:**
   ```
   https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates
   
   Thay <YOUR_BOT_TOKEN> bằng token từ BotFather
   ```

3. **Tìm Chat ID trong JSON:**
   ```json
   {
     "message": {
       "chat": {
         "id": 123456789  ← Đây là Chat ID
       }
     }
   }
   ```

## ⚙️ Bước 3: Cấu hình trong Code

Edit file `binance_config.py`:

```python
# ============================================================================
# TELEGRAM NOTIFICATIONS
# ============================================================================
TELEGRAM_BOT_TOKEN = "123456789:ABCdefGHIjklMNOpqrsTUVwxyz"  # Token từ BotFather
TELEGRAM_CHAT_ID = "123456789"                               # ID từ userinfobot
ENABLE_TELEGRAM = True  # Bật thông báo
```

## 🧪 Bước 4: Test Telegram

Chạy script test:

```python
from telegram_notifier import TelegramNotifier

bot_token = "YOUR_BOT_TOKEN"
chat_id = "YOUR_CHAT_ID"

telegram = TelegramNotifier(bot_token, chat_id)

if telegram.test_connection():
    print("✅ Telegram works!")
else:
    print("❌ Check your credentials")
```

Hoặc test trực tiếp:

```powershell
python -c "from telegram_notifier import TelegramNotifier; from binance_config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID; TelegramNotifier(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID).test_connection()"
```

## 📱 Thông báo sẽ nhận được:

### Khi bot start:
```
🚀 Trading Bot Started

Symbol: BTCUSDT
Capital: $10,000.00
Strategy: ADAPTIVE

⏰ 2026-01-31 17:30:00
```

### Khi mua (BUY):
```
🟢 BUY BTCUSDT

Quantity: 0.12
Price: $83,000.00

⏰ 2026-01-31 17:35:00
```

### Khi bán (SELL):
```
🔴 SELL BTCUSDT

Quantity: 0.12
Price: $84,992.00

💰 Profit: $238.40 (+2.40%)

⏰ 2026-01-31 17:45:00
```

### Status report (mỗi giờ):
```
📊 Bot Status Report

Symbol: BTCUSDT
Equity: $10,238.40
ROI: +2.38%
Open Positions: 2
Total Trades: 8
Total Profit: $238.40

⏰ 2026-01-31 18:00:00
```

## 🔒 Bảo mật Telegram Bot

1. **Chỉ bạn chat được với bot**
   - BotFather → /mybots → Chọn bot
   - Bot Settings → Allow Groups? → Disable

2. **Private bot**
   - Không share bot link
   - Chỉ bạn có Chat ID

3. **Không lưu token vào git**
   ```bash
   # Đã có trong .gitignore
   binance_config.py
   ```

## ❓ Troubleshooting

### "Unauthorized"
- Check bot token đúng chưa
- Đã nhắn `/start` cho bot chưa?

### "Chat not found"
- Check Chat ID đúng chưa
- Phải nhắn cho bot trước khi dùng API

### "Connection timeout"
- Check internet
- Telegram có bị block không?
- Thử dùng VPN

### Không nhận được message
- Đã enable ENABLE_TELEGRAM = True?
- Check bot token và chat ID
- Chạy test_connection()

## 📞 Support

**Telegram Bot API:**
- https://core.telegram.org/bots/api

**BotFather Commands:**
- `/mybots` - Quản lý bots
- `/setcommands` - Set bot commands
- `/setdescription` - Set description

---

**✅ Done! Bạn sẽ nhận thông báo Telegram mỗi khi bot trade!**
