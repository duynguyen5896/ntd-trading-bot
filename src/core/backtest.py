"""
Enhanced backtest engine with Binance fees
"""
import pandas as pd
from typing import Dict
from core.strategy import DynamicGridHedgeStrategy
from core.indicators import ema, atr
from datetime import datetime, timedelta


class BacktestEngine:
    """Backtest with realistic Binance fees"""
    
    def __init__(self, strategy: DynamicGridHedgeStrategy, data: pd.DataFrame, config: Dict):
        self.strategy = strategy
        self.data = data
        self.config = config
        self.equity_curve = []
        self.peak_equity = config['initial_capital']
        
    def run(self) -> Dict:
        """Run backtest"""
        print(f"\nRunning backtest on {len(self.data)} bars...")
        print(f"Period: {self.data.index[0]} to {self.data.index[-1]}")
        
        # Calculate indicators
        ema_values = ema(self.data['close'], self.config['ema_period'])
        atr_values = atr(self.data['high'], self.data['low'], self.data['close'], 
                        self.config['atr_period'])
        
        # Run backtest
        for idx, (timestamp, row) in enumerate(self.data.iterrows()):
            ema_val = ema_values.iloc[idx] if idx < len(ema_values) else row['close']
            atr_val = atr_values.iloc[idx] if idx < len(atr_values) else 0
            
            # Execute strategy
            self.strategy.execute(row, ema_val, atr_val, timestamp)
            
            # Track equity
            equity = self.strategy.state.equity(row['close'])
            spot_pnl, futures_pnl = self.strategy.state.unrealized_pnl(row['close'])
            
            self.equity_curve.append({
                'timestamp': timestamp,
                'price': row['close'],
                'open': row.get('open', row['close']),
                'high': row.get('high', row['close']),
                'low': row.get('low', row['close']),
                'close': row['close'],
                'equity': equity,
                'balance': self.strategy.state.balance,
                'spot_qty': self.strategy.state.spot_qty,
                'spot_value': self.strategy.state.spot_qty * row['close'],
                'spot_pnl': spot_pnl,
                'futures_short_qty': self.strategy.state.futures_short_qty,
                'futures_pnl': futures_pnl,
                'futures_margin': self.strategy.state.futures_margin,
                'total_fees': self.strategy.state.total_spot_fees + self.strategy.state.total_futures_fees,
                'funding_paid': self.strategy.state.total_funding_paid,
                'center_price': self.strategy.state.center_price,
                'ema': ema_val
            })
            
            # Update peak
            if equity > self.peak_equity:
                self.peak_equity = equity
            
            # Check drawdown
            drawdown = (equity - self.peak_equity) / self.peak_equity
            if drawdown < -self.config['max_drawdown']:
                print(f"\nMax drawdown reached: {drawdown*100:.2f}%")
                break
            
            # Check margin call
            if equity < self.config['initial_capital'] * self.config['margin_call_threshold']:
                print(f"\nMargin call threshold reached!")
                break
        
        # Final results
        final_price = self.data['close'].iloc[idx]
        final_equity = self.strategy.state.equity(final_price)
        final_state = self.strategy.get_state()
        
        print(f"\nBacktest completed: {len(self.equity_curve)} bars processed")
        print(f"Total trades: {len(final_state['trades'])}")
        
        return {
            'equity_curve': pd.DataFrame(self.equity_curve),
            'trades': pd.DataFrame(final_state['trades']),
            'final_equity': final_equity,
            'initial_capital': self.config['initial_capital'],
            'final_state': final_state,
            'final_price': final_price
        }
