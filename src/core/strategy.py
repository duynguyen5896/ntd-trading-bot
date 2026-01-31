"""
Optimized Grid + Hedge Strategy with Binance Fees
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from core.indicators import ema, atr


class BinanceFees:
    """Binance fee structure"""
    SPOT_MAKER = 0.001  # 0.1%
    SPOT_TAKER = 0.001  # 0.1%
    FUTURES_MAKER = 0.0002  # 0.02%
    FUTURES_TAKER = 0.0005  # 0.05%
    FUNDING_RATE_BASE = 0.0001  # 0.01% per 8h
    FUNDING_INTERVAL_HOURS = 8


class StrategyState:
    """Enhanced state with fees and funding tracking"""
    def __init__(self, balance: float):
        self.balance = balance
        self.initial_balance = balance
        
        # Spot positions
        self.spot_qty = 0.0
        self.spot_entries = []  # List of (price, qty)
        self.grid_levels_bought = set()
        
        # Futures positions
        self.futures_short_qty = 0.0
        self.futures_entry_price = 0.0
        self.futures_margin = 0.0
        self.hedge_layers = []
        
        # Tracking
        self.trades = []
        self.total_spot_fees = 0.0
        self.total_futures_fees = 0.0
        self.total_funding_paid = 0.0
        self.last_funding_time = None
        
        # Grid management
        self.center_price = 0.0
        self.grid_upper_bound = 0.0
        self.grid_lower_bound = 0.0
        
    def equity(self, price: float) -> float:
        """Calculate total equity including unrealized PnL"""
        spot_value = self.spot_qty * price
        futures_pnl = 0.0
        
        if self.futures_short_qty > 0:
            # Short PnL = entry_price * qty - current_price * qty
            futures_pnl = (self.futures_entry_price - price) * self.futures_short_qty
        
        return self.balance + spot_value + futures_pnl - self.futures_margin
    
    def unrealized_pnl(self, price: float) -> Tuple[float, float]:
        """Get spot and futures unrealized PnL separately"""
        spot_pnl = 0.0
        for entry_price, qty in self.spot_entries:
            spot_pnl += (price - entry_price) * qty
        
        futures_pnl = 0.0
        if self.futures_short_qty > 0:
            futures_pnl = (self.futures_entry_price - price) * self.futures_short_qty
        
        return spot_pnl, futures_pnl


class DynamicGridHedgeStrategy:
    """Optimized Grid + Hedge Strategy"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.state = StrategyState(config['initial_capital'])
        self.fees = BinanceFees()
        
    def initialize_grid(self, center_price: float):
        """Initialize dynamic grid around center price"""
        step = self.config['grid_step']
        levels = self.config['grid_levels']
        
        self.state.center_price = center_price
        self.state.grid_lower_bound = center_price * (1 - step * levels / 2)
        self.state.grid_upper_bound = center_price * (1 + step * levels / 2)
        
    def should_rebalance_grid(self, current_price: float, ema_price: float) -> bool:
        """Check if grid needs rebalancing"""
        threshold = self.config.get('rebalance_threshold', 0.05)
        distance = abs(current_price - self.state.center_price) / self.state.center_price
        
        return distance > threshold
    
    def rebalance_grid(self, new_center: float, timestamp):
        """Rebalance grid WITHOUT closing positions"""
        old_center = self.state.center_price
        self.initialize_grid(new_center)
        
        # Reset grid levels but keep positions
        self.state.grid_levels_bought.clear()
        
        self.state.trades.append({
            'timestamp': timestamp,
            'type': 'GRID_REBALANCE',
            'old_center': old_center,
            'new_center': new_center,
            'spot_qty': self.state.spot_qty,
            'note': 'Grid rebalanced without closing positions'
        })
    
    def grid_buy_logic(self, price: float, timestamp) -> bool:
        """Grid buy at levels below center"""
        step = self.config['grid_step']
        levels = self.config['grid_levels']
        
        for i in range(1, levels + 1):
            buy_price = self.state.center_price * (1 - i * step)
            
            if i not in self.state.grid_levels_bought and price <= buy_price and self.state.balance > 0:
                risk_cash = self.state.balance * self.config['grid_risk_per_order']
                qty = risk_cash / price
                fee = qty * price * self.fees.SPOT_TAKER
                total_cost = qty * price + fee
                
                if total_cost <= self.state.balance:
                    self.state.spot_qty += qty
                    self.state.balance -= total_cost
                    self.state.spot_entries.append((price, qty))
                    self.state.grid_levels_bought.add(i)
                    self.state.total_spot_fees += fee
                    
                    self.state.trades.append({
                        'timestamp': timestamp,
                        'type': 'GRID_BUY',
                        'level': i,
                        'price': price,
                        'qty': qty,
                        'cost': qty * price,
                        'fee': fee,
                        'balance': self.state.balance
                    })
                    return True
        return False
    
    def grid_sell_logic(self, price: float, timestamp) -> bool:
        """Grid sell with take profit"""
        take_profit_pct = self.config.get('grid_take_profit', 0.012)
        sold = False
        
        for entry_price, qty in self.state.spot_entries.copy():
            if price >= entry_price * (1 + take_profit_pct):
                revenue = qty * price
                fee = revenue * self.fees.SPOT_TAKER
                net_revenue = revenue - fee
                profit = net_revenue - (qty * entry_price)
                
                self.state.balance += net_revenue
                self.state.spot_qty -= qty
                self.state.spot_entries.remove((entry_price, qty))
                self.state.total_spot_fees += fee
                
                # Allow rebuy at this level
                # (grid level will be available again)
                
                self.state.trades.append({
                    'timestamp': timestamp,
                    'type': 'GRID_SELL',
                    'entry_price': entry_price,
                    'exit_price': price,
                    'qty': qty,
                    'revenue': revenue,
                    'fee': fee,
                    'profit': profit,
                    'balance': self.state.balance
                })
                sold = True
        
        return sold
    
    def hedge_logic(self, price: float, atr_value: float, timestamp):
        """Dynamic hedge based on ATR distance"""
        if atr_value == 0 or self.state.center_price == 0:
            return
        
        distance_atr = abs(price - self.state.center_price) / atr_value
        equity = self.state.equity(price)
        leverage = self.config.get('hedge_leverage', 3)
        
        thresholds = self.config['hedge_atr_threshold']
        sizes = self.config['hedge_sizes']
        
        # Open hedge layers
        for threshold, size in zip(thresholds, sizes):
            if distance_atr > threshold and threshold not in self.state.hedge_layers:
                # Only hedge if price moved DOWN (protection against dump)
                if price < self.state.center_price:
                    hedge_value = equity * size
                    qty = (hedge_value * leverage) / price
                    fee = qty * price * self.fees.FUTURES_TAKER
                    margin_required = (qty * price) / leverage
                    
                    if margin_required < self.state.balance * 0.3:  # Max 30% balance as margin
                        # Update average entry price
                        total_qty = self.state.futures_short_qty + qty
                        if self.state.futures_short_qty > 0:
                            self.state.futures_entry_price = (
                                (self.state.futures_entry_price * self.state.futures_short_qty + price * qty) / total_qty
                            )
                        else:
                            self.state.futures_entry_price = price
                        
                        self.state.futures_short_qty = total_qty
                        self.state.futures_margin += margin_required
                        self.state.balance -= fee
                        self.state.total_futures_fees += fee
                        self.state.hedge_layers.append(threshold)
                        
                        self.state.trades.append({
                            'timestamp': timestamp,
                            'type': 'HEDGE_OPEN',
                            'layer': threshold,
                            'price': price,
                            'qty': qty,
                            'leverage': leverage,
                            'margin': margin_required,
                            'fee': fee,
                            'distance_atr': distance_atr
                        })
        
        # Close hedge layers when price recovers
        if self.state.hedge_layers and distance_atr < min(thresholds) - 0.5:
            # Close all hedge
            if self.state.futures_short_qty > 0:
                pnl = (self.state.futures_entry_price - price) * self.state.futures_short_qty
                fee = self.state.futures_short_qty * price * self.fees.FUTURES_TAKER
                net_pnl = pnl - fee
                
                self.state.balance += net_pnl + self.state.futures_margin - fee
                self.state.total_futures_fees += fee
                
                self.state.trades.append({
                    'timestamp': timestamp,
                    'type': 'HEDGE_CLOSE_ALL',
                    'exit_price': price,
                    'qty': self.state.futures_short_qty,
                    'entry_price': self.state.futures_entry_price,
                    'pnl': pnl,
                    'fee': fee,
                    'net_pnl': net_pnl
                })
                
                self.state.futures_short_qty = 0.0
                self.state.futures_entry_price = 0.0
                self.state.futures_margin = 0.0
                self.state.hedge_layers.clear()
    
    def apply_funding_rate(self, timestamp, price: float):
        """Apply funding rate every 8 hours"""
        if self.state.last_funding_time is None:
            self.state.last_funding_time = timestamp
            return
        
        hours_elapsed = (timestamp - self.state.last_funding_time).total_seconds() / 3600
        
        if hours_elapsed >= self.fees.FUNDING_INTERVAL_HOURS:
            if self.state.futures_short_qty > 0:
                position_value = self.state.futures_short_qty * price
                funding = position_value * self.fees.FUNDING_RATE_BASE
                
                # Short pays funding (usually)
                self.state.balance -= funding
                self.state.total_funding_paid += funding
                
                self.state.last_funding_time = timestamp
    
    def execute(self, bar: pd.Series, ema_value: float, atr_value: float, timestamp):
        """Execute strategy for one bar"""
        price = bar['close']
        
        # Initialize grid on first bar
        if self.state.center_price == 0:
            self.initialize_grid(ema_value)
        
        # Apply funding rate
        self.apply_funding_rate(timestamp, price)
        
        # Rebalance grid if needed
        if self.should_rebalance_grid(price, ema_value):
            self.rebalance_grid(ema_value, timestamp)
        
        # Execute grid logic
        self.grid_buy_logic(price, timestamp)
        self.grid_sell_logic(price, timestamp)
        
        # Execute hedge logic
        self.hedge_logic(price, atr_value, timestamp)
    
    def get_state(self) -> Dict:
        """Get current state snapshot"""
        return {
            'balance': self.state.balance,
            'spot_qty': self.state.spot_qty,
            'futures_short_qty': self.state.futures_short_qty,
            'futures_margin': self.state.futures_margin,
            'spot_entries': len(self.state.spot_entries),
            'hedge_layers': self.state.hedge_layers.copy(),
            'trades': self.state.trades.copy(),
            'total_fees': self.state.total_spot_fees + self.state.total_futures_fees,
            'total_funding': self.state.total_funding_paid,
            'center_price': self.state.center_price
        }
