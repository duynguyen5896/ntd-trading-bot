# Deploy Trading Bot lên PythonAnywhere (FREE - Không cần Credit Card)

## ✅ Ưu điểm:
- Hoàn toàn FREE
- KHÔNG cần thẻ tín dụng
- Chạy 24/7
- Python native
- Binance API whitelisted

## 📋 Bước 1: Đăng ký Account

1. Vào: https://www.pythonanywhere.com/registration/register/beginner/
2. Chọn **Beginner** (FREE)
3. Điền thông tin:
   - Username
   - Email
   - Password
4. Verify email
5. Login

## 📁 Bước 2: Upload Code

### Option A: Upload qua Web UI (Dễ nhất)

1. Click **Files** tab
2. Click **Upload a file**
3. Upload từng file:
   - `binance_config.py` (nhớ điền API keys!)
   - `binance_connector.py`
   - `live_trading_bot.py`
   - `start_live_trading.py`
4. Tạo folder `configs/`:
   - New directory: `configs`
   - Upload `strategy_configs.py`
5. Tạo folder `core/`:
   - New directory: `core`
   - Upload `indicators.py`, `strategy.py`, `backtest.py`, `performance.py`

### Option B: Upload qua Git (Nhanh hơn)

1. Click **Consoles** → **Bash**
2. Commands:
```bash
git clone <your-github-repo-url>
cd isve_backtest
```

## 🔧 Bước 3: Cài đặt Packages

1. Click **Consoles** → **Bash**
2. Chạy:
```bash
pip3 install --user python-binance pandas numpy matplotlib
```

3. Verify:
```bash
python3 -c "import binance; print('OK')"
```

## ⚙️ Bước 4: Cấu hình Bot

1. Edit `binance_config.py`:
```bash
# Click Files → binance_config.py → Edit
# Paste API keys của bạn
```

2. Test connection:
```bash
python3 test_binance_connection.py
```

## 🚀 Bước 5: Chạy Bot

### Chạy tạm thời (test):
```bash
python3 start_live_trading.py
```

### Chạy Always-On (24/7):

**⚠️ FREE account giới hạn:**
- Chỉ 1 "Always-on task"
- Phải restart manual mỗi 24h

**Tạo Always-on Task:**
1. Click **Tasks** tab
2. Create scheduled task:
   - Command: `/home/your_username/.local/bin/python3 /home/your_username/isve_backtest/start_live_trading.py`
   - Hour: `00` (midnight)
   - Minute: `00`

**Hoặc dùng screen:**
```bash
# Bash console
screen -S trading_bot
cd isve_backtest
python3 start_live_trading.py

# Press Ctrl+A, D to detach
# Bot chạy background
```

**Reattach:**
```bash
screen -r trading_bot
```

## 📊 Bước 6: Monitor Bot

### Check logs:
```bash
# Bash console
tail -f bot.log
```

### Check processes:
```bash
ps aux | grep python
```

### Stop bot:
```bash
pkill -f start_live_trading.py
```

## 🔍 Troubleshooting

### 1. "Permission denied"
```bash
chmod +x start_live_trading.py
```

### 2. "Module not found"
```bash
pip3 install --user <package-name>
```

### 3. "API connection failed"
- Check `binance_config.py` có API keys
- Verify testnet mode: `USE_TESTNET = True`

### 4. "Task không chạy"
- FREE account chỉ 1 always-on task
- Dùng `screen` thay thế

## 💡 Tips PythonAnywhere

### Giữ bot chạy 24/7:
```bash
# Create keepalive script
nano keepalive.sh
```

```bash
#!/bin/bash
while true; do
    python3 /home/username/isve_backtest/start_live_trading.py
    echo "Bot stopped, restarting in 10s..."
    sleep 10
done
```

```bash
chmod +x keepalive.sh
screen -S bot -dm ./keepalive.sh
```

### Monitor từ xa:
```python
# Thêm vào bot: gửi email khi có trade
import smtplib
# Send notification
```

## ⚠️ Giới hạn FREE Account:

- ✅ 512MB RAM (đủ cho bot)
- ✅ 100MB disk (đủ cho code + logs)
- ✅ CPU: 100s/day limit (bot trading ít CPU)
- ⚠️ Không SSH (chỉ web console)
- ⚠️ Phải restart manual mỗi 24h

## 🎯 Upgrade Options:

Nếu cần 24/7 thật sự:
- **Hacker Plan**: $5/tháng
  - Always-on tasks unlimited
  - No manual restart
  - More CPU

## 📞 Support

**PythonAnywhere Help:**
- https://help.pythonanywhere.com/

**Binance Testnet:**
- https://testnet.binance.vision/

## ✅ Checklist Deployment

- [ ] Đăng ký PythonAnywhere FREE
- [ ] Upload all files
- [ ] Install `python-binance`
- [ ] Config `binance_config.py` with API keys
- [ ] Test connection: `python3 test_binance_connection.py`
- [ ] Run bot: `python3 start_live_trading.py`
- [ ] Setup screen session cho 24/7
- [ ] Monitor logs
- [ ] Test với testnet trước

---

**🎉 Done! Bot trading của bạn đang chạy FREE trên cloud!**
