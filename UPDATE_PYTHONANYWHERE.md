# Update Code lên PythonAnywhere

## 🔄 3 Cách Update Code:

### 1️⃣ Upload qua Web UI (Dễ nhất)

**Bước 1: Vào Files**
1. Login: https://www.pythonanywhere.com/
2. Click tab **Files**
3. Navigate đến folder project

**Bước 2: Upload file đã thay đổi**
- Click file cũ → Delete
- Upload file mới
- Hoặc click file → Edit → Paste code mới

**Files cần update khi thêm Telegram:**
```
✅ binance_config.py (thêm TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID)
✅ live_trading_bot.py (đã tích hợp Telegram)
✅ start_live_trading.py (đã tích hợp Telegram)
📄 telegram_notifier.py (file mới)
```

**Bước 3: Install package mới**
```bash
# Bash console
pip3 install --user requests
```

### 2️⃣ Git Pull (Nhanh, cho ai dùng Git)

**Setup lần đầu:**
```bash
# Bash console
cd ~
git clone https://github.com/your-username/your-repo.git
cd your-repo
```

**Update sau này:**
```bash
# Bash console
cd ~/your-repo
git pull origin main
pip3 install --user -r requirements.txt
```

**Restart bot:**
```bash
pkill -f start_live_trading.py
screen -S bot
python3 start_live_trading.py
```

### 3️⃣ rsync/scp (Cho advanced users)

**Từ máy local:**
```bash
# Upload 1 file
scp live_trading_bot.py username@ssh.pythonanywhere.com:~/isve_backtest/

# Upload cả folder
rsync -avz isve_backtest/ username@ssh.pythonanywhere.com:~/isve_backtest/
```

⚠️ **FREE account không có SSH**. Cần **Hacker plan ($5/mo)** mới dùng được.

## 📦 Update Telegram Integration

### Bước chi tiết:

**1. Tạo Telegram Bot** (xem TELEGRAM_SETUP.md)
   - Vào @BotFather
   - /newbot
   - Copy bot token

**2. Lấy Chat ID**
   - Vào @userinfobot
   - /start
   - Copy chat ID

**3. Update binance_config.py trên PythonAnywhere**

```bash
# Option A: Web UI
Files → binance_config.py → Edit
```

Thêm vào:
```python
# TELEGRAM NOTIFICATIONS
TELEGRAM_BOT_TOKEN = "your_bot_token_here"
TELEGRAM_CHAT_ID = "your_chat_id_here"
ENABLE_TELEGRAM = True
```

**4. Upload file mới**

```bash
# Files tab
- Upload telegram_notifier.py
- Replace live_trading_bot.py
- Replace start_live_trading.py
```

**5. Install requests package**

```bash
# Bash console
pip3 install --user requests
```

**6. Test Telegram**

```bash
# Bash console
python3 -c "from telegram_notifier import TelegramNotifier; from binance_config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID; print('✅ OK' if TelegramNotifier(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID).test_connection() else '❌ Failed')"
```

**7. Restart bot**

```bash
# Stop old bot
pkill -f start_live_trading.py

# Start new bot with Telegram
screen -S bot
python3 start_live_trading.py
# Ctrl+A, D to detach
```

## 🔄 Workflow Update thường xuyên:

### Khi sửa strategy/config:

```bash
# 1. Stop bot
pkill -f start_live_trading.py

# 2. Update file (web UI hoặc git pull)
# Upload file đã sửa

# 3. Restart
screen -S bot
python3 start_live_trading.py
```

### Khi thêm tính năng mới:

```bash
# 1. Upload file mới
# 2. Install packages (nếu cần)
pip3 install --user <package>

# 3. Test
python3 test_new_feature.py

# 4. Restart bot
pkill -f start_live_trading.py
screen -S bot
python3 start_live_trading.py
```

## 🚀 Script tự động update (Advanced)

Tạo file `update.sh` trên PythonAnywhere:

```bash
#!/bin/bash
# update.sh

echo "Stopping bot..."
pkill -f start_live_trading.py

echo "Pulling latest code..."
cd ~/isve_backtest
git pull origin main

echo "Installing packages..."
pip3 install --user -r requirements.txt

echo "Starting bot..."
screen -S bot -dm python3 start_live_trading.py

echo "✅ Update complete!"
screen -ls
```

Chạy:
```bash
chmod +x update.sh
./update.sh
```

## 📋 Checklist Update Telegram:

- [ ] Tạo Telegram bot (@BotFather)
- [ ] Lấy Chat ID (@userinfobot)
- [ ] Update `binance_config.py` với credentials
- [ ] Upload `telegram_notifier.py`
- [ ] Upload `live_trading_bot.py` (updated)
- [ ] Upload `start_live_trading.py` (updated)
- [ ] Install requests: `pip3 install --user requests`
- [ ] Test Telegram connection
- [ ] Restart bot
- [ ] Verify nhận được thông báo "Bot Started"

## ⚠️ Lưu ý quan trọng:

1. **Backup trước khi update**
   ```bash
   # Download file cũ trước khi replace
   ```

2. **Test local trước**
   ```bash
   # Test trên máy Windows trước
   python start_live_trading.py
   ```

3. **Check logs sau update**
   ```bash
   # Xem có lỗi không
   tail -f ~/.local/share/pythonanywhere/error.log
   ```

4. **Screen session**
   ```bash
   # List sessions
   screen -ls
   
   # Reattach
   screen -r bot
   
   # Kill old session
   screen -X -S bot quit
   ```

## 📱 Verify Telegram hoạt động:

Sau khi restart bot, check Telegram:

1. **Nhận "Bot Started"** ✅
2. **Khi có trade, nhận thông báo BUY/SELL** ✅
3. **Mỗi giờ nhận Status Report** ✅
4. **Khi stop bot, nhận "Bot Stopped"** ✅

---

**🎉 Done! Code đã update và Telegram đã hoạt động!**
