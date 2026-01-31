"""
Telegram Bot Notifications for Trading Bot
"""
import requests
from datetime import datetime
from typing import Optional

class TelegramNotifier:
    """Send trading notifications to Telegram"""
    
    def __init__(self, bot_token: str, chat_id: str):
        """
        Initialize Telegram notifier
        
        Args:
            bot_token: Telegram bot token from @BotFather
            chat_id: Your chat ID or channel ID (e.g., '-1001234567890' for channel)
                    - Personal chat: positive number
                    - Group: negative number starting with -
                    - Channel: negative number starting with -100
        """
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{bot_token}"
        
    def send_message(self, message: str, parse_mode: str = "HTML") -> bool:
        """Send message to Telegram"""
        try:
            url = f"{self.base_url}/sendMessage"
            data = {
                "chat_id": self.chat_id,
                "text": message,
                "parse_mode": parse_mode
            }
            response = requests.post(url, data=data, timeout=10)
            return response.status_code == 200
        except Exception as e:
            print(f"⚠️ Telegram notification failed: {e}")
            return False
    
    def notify_trade(self, trade_type: str, symbol: str, quantity: float, 
                    price: float, profit: Optional[float] = None):
        """
        Notify about trade execution
        
        Args:
            trade_type: 'BUY' or 'SELL'
            symbol: Trading pair (e.g., 'BTCUSDT')
            quantity: Trade quantity
            price: Execution price
            profit: Profit amount (for SELL only)
        """
        icon = "🟢" if trade_type == "BUY" else "🔴"
        
        message = f"{icon} <b>{trade_type} {symbol}</b>\n\n"
        message += f"Quantity: <code>{quantity}</code>\n"
        message += f"Price: <code>${price:,.2f}</code>\n"
        
        if profit is not None:
            profit_pct = (profit / (quantity * price)) * 100
            message += f"\n💰 Profit: <code>${profit:+,.2f}</code> ({profit_pct:+.2f}%)\n"
        
        message += f"\n⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        return self.send_message(message)
    
    def notify_status(self, symbol: str, equity: float, roi: float, 
                     positions: int, total_trades: int, total_profit: float):
        """Send bot status update"""
        message = f"📊 <b>Bot Status Report</b>\n\n"
        message += f"Symbol: <code>{symbol}</code>\n"
        message += f"Equity: <code>${equity:,.2f}</code>\n"
        message += f"ROI: <code>{roi:+.2f}%</code>\n"
        message += f"Open Positions: <code>{positions}</code>\n"
        message += f"Total Trades: <code>{total_trades}</code>\n"
        message += f"Total Profit: <code>${total_profit:+,.2f}</code>\n"
        message += f"\n⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        return self.send_message(message)
    
    def notify_start(self, symbol: str, capital: float, config: str):
        """Notify bot started"""
        message = f"🚀 <b>Trading Bot Started</b>\n\n"
        message += f"Symbol: <code>{symbol}</code>\n"
        message += f"Capital: <code>${capital:,.2f}</code>\n"
        message += f"Strategy: <code>{config}</code>\n"
        message += f"\n⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        return self.send_message(message)
    
    def notify_stop(self, symbol: str, start_equity: float, 
                   final_equity: float, total_trades: int, total_profit: float):
        """Notify bot stopped"""
        roi = ((final_equity - start_equity) / start_equity) * 100
        
        message = f"⏸️ <b>Trading Bot Stopped</b>\n\n"
        message += f"Symbol: <code>{symbol}</code>\n"
        message += f"Start Equity: <code>${start_equity:,.2f}</code>\n"
        message += f"Final Equity: <code>${final_equity:,.2f}</code>\n"
        message += f"ROI: <code>{roi:+.2f}%</code>\n"
        message += f"Total Trades: <code>{total_trades}</code>\n"
        message += f"Total Profit: <code>${total_profit:+,.2f}</code>\n"
        message += f"\n⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        return self.send_message(message)
    
    def notify_error(self, error_msg: str):
        """Notify about errors"""
        message = f"❌ <b>Bot Error</b>\n\n"
        message += f"<code>{error_msg}</code>\n"
        message += f"\n⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        return self.send_message(message)
    
    def notify_warning(self, warning_msg: str):
        """Notify about warnings"""
        message = f"⚠️ <b>Warning</b>\n\n"
        message += f"{warning_msg}\n"
        message += f"\n⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        return self.send_message(message)
    
    def test_connection(self) -> bool:
        """Test Telegram connection"""
        try:
            message = "✅ <b>Telegram Bot Connected!</b>\n\n"
            message += "Trading bot notifications are ready."
            return self.send_message(message)
        except Exception as e:
            print(f"❌ Telegram test failed: {e}")
            return False
