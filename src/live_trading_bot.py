"""
Live Trading Bot for Binance - Grid + Hedge Strategy
WARNING: This bot places REAL orders on Binance (testnet or live)
"""
import time
from datetime import datetime
from typing import Dict, List, Optional
import pandas as pd
from src.binance_connector import BinanceTradingBot
from src.configs.strategy_configs import CONFIG_ADAPTIVE
from src.core.indicators import ema, atr
from src.telegram_notifier import TelegramNotifier

class LiveGridHedgeBot:
    """Live trading bot implementing Grid + Hedge strategy"""
    
    def __init__(self, bot: BinanceTradingBot, symbol: str, config: Dict,
                 telegram: Optional[TelegramNotifier] = None):
        self.bot = bot
        self.symbol = symbol
        self.config = config
        self.telegram = telegram
        
        # State
        self.is_running = False
        self.equity = config['initial_capital']
        self.start_equity = config['initial_capital']
        self.peak_equity = config['initial_capital']
        
        # Grid tracking
        self.grid_positions = {}  # price -> quantity
        self.grid_center = 0.0
        
        # Hedge tracking  
        self.hedge_positions = []
        
        # Historical data
        self.price_history = []
        self.max_history = 200
        
        # Trading stats
        self.total_trades = 0
        self.total_profit = 0.0
        self.total_fees = 0.0
        
    def initialize(self) -> bool:
        """Initialize bot - download initial data"""
        print(f"\n{'='*70}")
        print(f"INITIALIZING LIVE BOT: {self.symbol}")
        print(f"{'='*70}")
        
        # Download historical data for indicators
        df = self.bot.get_historical_data(
            self.symbol, 
            interval='1h', 
            days=7
        )
        
        if df.empty:
            print("❌ Failed to download initial data")
            return False
        
        # Initialize price history
        self.price_history = df['close'].tolist()[-self.max_history:]
        
        # Calculate initial grid center (EMA50)
        ema_values = ema(pd.Series(self.price_history), self.config['ema_period'])
        self.grid_center = ema_values.iloc[-1]
        
        print(f"✅ Initial data loaded: {len(self.price_history)} bars")
        print(f"Grid center (EMA50): ${self.grid_center:,.2f}")
        
        # Get initial balance
        balance = self.bot.get_account_balance('USDT')
        print(f"Available USDT: ${balance:,.2f}")
        
        if balance < 100:
            print("⚠️ WARNING: Low balance. Get testnet funds at https://testnet.binance.vision/")
        
        return True
    
    def update_price(self) -> float:
        """Get current price and update history"""
        price = self.bot.get_price(self.symbol)
        
        if price > 0:
            self.price_history.append(price)
            if len(self.price_history) > self.max_history:
                self.price_history.pop(0)
        
        return price
    
    def update_indicators(self):
        """Recalculate indicators"""
        if len(self.price_history) < self.config['ema_period']:
            return
        
        prices = pd.Series(self.price_history)
        ema_values = ema(prices, self.config['ema_period'])
        self.grid_center = ema_values.iloc[-1]
    
    def should_buy_grid(self, price: float) -> bool:
        """Check if should place grid buy order"""
        if price >= self.grid_center:
            return False
        
        # Check grid step
        grid_step = self.config['grid_step']
        distance = abs(price - self.grid_center) / self.grid_center
        
        # Check if price is at grid level
        is_at_grid = (distance % grid_step) < (grid_step * 0.1)
        
        # Check if not already bought at this level
        already_bought = any(
            abs(p - price) / price < grid_step * 0.5 
            for p in self.grid_positions.keys()
        )
        
        return is_at_grid and not already_bought
    
    def should_sell_grid(self, price: float) -> List[float]:
        """Check which grid positions should be closed"""
        to_close = []
        take_profit = self.config['grid_take_profit']
        
        for buy_price, qty in self.grid_positions.items():
            profit_pct = (price - buy_price) / buy_price
            if profit_pct >= take_profit:
                to_close.append(buy_price)
        
        return to_close
    
    def calculate_position_size(self, price: float) -> float:
        """Calculate position size based on risk"""
        balance = self.bot.get_account_balance('USDT')
        risk_per_order = self.config['grid_risk_per_order']
        
        position_value = balance * risk_per_order
        quantity = position_value / price
        
        # Round to symbol precision (for BTC: 5 decimals)
        quantity = round(quantity, 5)
        
        # Check minimum notional ($10 for Binance)
        if quantity * price < 10:
            return 0.0
        
        return quantity
    
    def place_grid_buy(self, price: float):
        """Place grid buy order"""
        quantity = self.calculate_position_size(price)
        
        if quantity == 0:
            print(f"⚠️ Position size too small at ${price:,.2f}")
            return
        
        print(f"\n🟢 GRID BUY: {quantity} {self.symbol} @ ${price:,.2f}")
        
        order = self.bot.place_market_order(self.symbol, 'BUY', quantity)
        
        if order:
            self.grid_positions[price] = quantity
            self.total_trades += 1
            print(f"✅ Grid position opened: ${price:,.2f}")
            
            # Calculate executed price
            executed_price = price
            if 'cummulativeQuoteQty' in order and 'executedQty' in order:
                try:
                    quote_qty = float(order['cummulativeQuoteQty'])
                    exec_qty = float(order['executedQty'])
                    if exec_qty > 0:
                        executed_price = quote_qty / exec_qty
                except Exception as e:
                    print(f"⚠️ Failed to calc executed price: {e}")

            # Get current balance
            current_balance = self.bot.get_account_balance('USDT')
            
            # Send Telegram notification
            if self.telegram:
                self.telegram.notify_trade(
                    'BUY', self.symbol, quantity, executed_price, current_balance
                )
    
    def close_grid_position(self, buy_price: float, current_price: float):
        """Close a grid position"""
        if buy_price not in self.grid_positions:
            return
        
        quantity = self.grid_positions[buy_price]
        profit_pct = ((current_price - buy_price) / buy_price) * 100
        
        print(f"\n🔴 GRID SELL: {quantity} {self.symbol} @ ${current_price:,.2f}")
        print(f"Profit: {profit_pct:+.2f}%")
        
        order = self.bot.place_market_order(self.symbol, 'SELL', quantity)
        
        if order:
            profit = (current_price - buy_price) * quantity
            self.total_profit += profit
            del self.grid_positions[buy_price]
            self.total_trades += 1
            print(f"✅ Grid closed: ${profit:+.2f} profit")
            
            # Calculate executed price
            executed_price = current_price
            if 'cummulativeQuoteQty' in order and 'executedQty' in order:
                try:
                    quote_qty = float(order['cummulativeQuoteQty'])
                    exec_qty = float(order['executedQty'])
                    if exec_qty > 0:
                        executed_price = quote_qty / exec_qty
                except Exception as e:
                    print(f"⚠️ Failed to calc executed price: {e}")

            # Get current balance
            current_balance = self.bot.get_account_balance('USDT')

            # Send Telegram notification
            if self.telegram:
                self.telegram.notify_trade(
                    'SELL', self.symbol, quantity, executed_price, current_balance, profit
                )
    
    def update_equity(self, current_price: float):
        """Calculate current equity"""
        balance = self.bot.get_account_balance('USDT')
        
        # Calculate market value of open positions
        position_value = sum(
            qty * current_price 
            for qty in self.grid_positions.values()
        )
        
        self.equity = balance + position_value
        
        # Update peak
        if self.equity > self.peak_equity:
            self.peak_equity = self.equity
    
    def check_risk_limits(self) -> bool:
        """Check if risk limits exceeded"""
        # Check drawdown
        if self.peak_equity > 0:
            drawdown = (self.peak_equity - self.equity) / self.peak_equity
            if drawdown > self.config['max_drawdown']:
                print(f"\n⛔ MAX DRAWDOWN REACHED: {drawdown:.2%}")
                return False
        
        return True
    
    def display_status(self, price: float):
        """Display current bot status"""
        roi = ((self.equity - self.start_equity) / self.start_equity) * 100
        drawdown = ((self.peak_equity - self.equity) / self.peak_equity) * 100 if self.peak_equity > 0 else 0
        
        print(f"\n{'='*70}")
        print(f"BOT STATUS - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*70}")
        print(f"Symbol: {self.symbol}")
        print(f"Current Price: ${price:,.2f}")
        print(f"Grid Center (EMA50): ${self.grid_center:,.2f}")
        print(f"\n💰 Equity:")
        print(f"  Start: ${self.start_equity:,.2f}")
        print(f"  Current: ${self.equity:,.2f}")
        print(f"  ROI: {roi:+.2f}%")
        print(f"  Drawdown: {drawdown:.2f}%")
        print(f"\n📊 Positions:")
        print(f"  Grid Positions: {len(self.grid_positions)}")
        if self.grid_positions:
            for buy_price, qty in self.grid_positions.items():
                pnl = (price - buy_price) * qty
                pnl_pct = ((price - buy_price) / buy_price) * 100
                print(f"    ${buy_price:,.2f}: {qty} ({pnl_pct:+.2f}% = ${pnl:+.2f})")
        print(f"\n📈 Trading Stats:")
        print(f"  Total Trades: {self.total_trades}")
        print(f"  Total Profit: ${self.total_profit:+,.2f}")
        print(f"{'='*70}")
    
    def run_cycle(self):
        """Execute one trading cycle"""
        # Get current price
        price = self.update_price()
        if price == 0:
            print("⚠️ Failed to get price")
            return
        
        # Update indicators
        self.update_indicators()
        
        # Update equity
        self.update_equity(price)
        
        # Check risk limits
        if not self.check_risk_limits():
            print("⛔ Risk limits exceeded - stopping bot")
            self.is_running = False
            return
        
        # Grid buy logic
        if self.should_buy_grid(price):
            self.place_grid_buy(price)
        
        # Grid sell logic
        positions_to_close = self.should_sell_grid(price)
        for buy_price in positions_to_close:
            self.close_grid_position(buy_price, price)
        
        # Concise status log
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Price: ${price:,.2f} | Eq: ${self.equity:,.2f} | Pos: {len(self.grid_positions)}")
    
    def start(self, check_interval: int = 60):
        """
        Start live trading bot
        
        Args:
            check_interval: Seconds between checks (default 60 = 1 minute)
        """
        print(f"\n{'='*70}")
        print("🚀 STARTING LIVE TRADING BOT")
        print(f"{'='*70}")
        print(f"Symbol: {self.symbol}")
        print(f"Check interval: {check_interval} seconds")
        print(f"Strategy: Grid + Hedge (ADAPTIVE)")
        print(f"\n⚠️ Press Ctrl+C to stop the bot")
        print(f"{'='*70}\n")
        
        self.is_running = True
        
        # Send start notification
        if self.telegram:
            self.telegram.notify_start(
                self.symbol, 
                self.start_equity,
                'ADAPTIVE'
            )
        
        try:
            cycle_count = 0
            while self.is_running:
                self.run_cycle()
                cycle_count += 1
                
                # Send status update every 60 minutes (60 cycles if interval=60s)
                if cycle_count % 60 == 0 and self.telegram:
                    roi = ((self.equity - self.start_equity) / self.start_equity) * 100
                    self.telegram.notify_status(
                        self.symbol, self.equity, roi,
                        len(self.grid_positions), self.total_trades, self.total_profit
                    )
                
                # Wait for next cycle
                # print(f"\n⏳ Next check in {check_interval} seconds...")
                time.sleep(check_interval)
                
        except KeyboardInterrupt:
            print("\n\n⏸️ Bot stopped by user")
        except Exception as e:
            print(f"\n\n❌ Bot error: {e}")
            if self.telegram:
                self.telegram.notify_error(str(e))
            import traceback
            traceback.print_exc()
        finally:
            self.stop()
    
    def stop(self):
        """Stop bot and show final stats"""
        self.is_running = False
        
        print(f"\n{'='*70}")
        print("📊 FINAL TRADING SUMMARY")
        print(f"{'='*70}")
        
        roi = ((self.equity - self.start_equity) / self.start_equity) * 100
        
        print(f"Start Equity: ${self.start_equity:,.2f}")
        print(f"Final Equity: ${self.equity:,.2f}")
        print(f"ROI: {roi:+.2f}%")
        print(f"Total Trades: {self.total_trades}")
        print(f"Total Profit: ${self.total_profit:+,.2f}")
        print(f"Open Grid Positions: {len(self.grid_positions)}")
        
        if self.grid_positions:
            print(f"\n⚠️ WARNING: {len(self.grid_positions)} positions still open!")
            print("Close manually or restart bot to manage them.")
        
        print(f"{'='*70}\n")
        
        # Send stop notification
        if self.telegram:
            self.telegram.notify_stop(
                self.symbol, self.start_equity, self.equity,
                self.total_trades, self.total_profit
            )
