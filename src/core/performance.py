"""
Enhanced performance analyzer with OHLC candlestick charts
"""
import pandas as pd
import numpy as np
from typing import Dict
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import matplotlib.dates as mdates


class PerformanceAnalyzer:
    """Analyze backtest with detailed metrics"""
    
    def __init__(self, results: Dict, config: Dict):
        self.results = results
        self.config = config
        self.equity_curve = results['equity_curve']
        self.trades = results['trades']
        self.initial_capital = results['initial_capital']
        self.final_equity = results['final_equity']
        self.final_state = results['final_state']
        self.backtest_days = config.get('backtest_days', 30)
        
    def calculate_metrics(self) -> Dict:
        """Calculate all performance metrics"""
        # ROI
        roi = ((self.final_equity - self.initial_capital) / self.initial_capital) * 100
        roi_monthly = (roi / self.backtest_days) * 30
        
        # Max Drawdown
        equity_series = self.equity_curve['equity']
        running_max = equity_series.expanding().max()
        drawdown_series = (equity_series - running_max) / running_max * 100
        max_dd = drawdown_series.min()
        
        # Sharpe Ratio
        returns = equity_series.pct_change().dropna()
        if len(returns) > 0 and returns.std() > 0:
            sharpe = np.sqrt(24 * 365) * returns.mean() / returns.std()  # Annualized
        else:
            sharpe = 0
        
        # Trade stats
        grid_buys = len(self.trades[self.trades['type'] == 'GRID_BUY'])
        grid_sells = len(self.trades[self.trades['type'] == 'GRID_SELL'])
        
        total_grid_profit = 0
        win_trades = 0
        if grid_sells > 0:
            profit_trades = self.trades[self.trades['type'] == 'GRID_SELL']
            total_grid_profit = profit_trades['profit'].sum()
            win_trades = len(profit_trades[profit_trades['profit'] > 0])
        
        win_rate = (win_trades / grid_sells * 100) if grid_sells > 0 else 0
        
        # Fees
        total_fees = self.final_state.get('total_fees', 0)
        total_funding = self.final_state.get('total_funding', 0)
        
        # Hedge stats
        hedge_opens = len(self.trades[self.trades['type'] == 'HEDGE_OPEN'])
        hedge_closes = len(self.trades[self.trades['type'] == 'HEDGE_CLOSE_ALL'])
        
        hedge_pnl = 0
        if hedge_closes > 0:
            hedge_pnl = self.trades[self.trades['type'] == 'HEDGE_CLOSE_ALL']['net_pnl'].sum()
        
        return {
            'roi': roi,
            'roi_monthly': roi_monthly,
            'max_drawdown': max_dd,
            'sharpe_ratio': sharpe,
            'grid_buys': grid_buys,
            'grid_sells': grid_sells,
            'grid_profit': total_grid_profit,
            'win_rate': win_rate,
            'hedge_opens': hedge_opens,
            'hedge_closes': hedge_closes,
            'hedge_pnl': hedge_pnl,
            'total_fees': total_fees,
            'total_funding': total_funding,
        }
    
    def print_report(self):
        """Print comprehensive performance report"""
        metrics = self.calculate_metrics()
        
        print("\n" + "="*70)
        print("GRID + HEDGE STRATEGY PERFORMANCE REPORT")
        print("="*70)
        
        # Capital & Returns
        print(f"\n📊 CAPITAL & RETURNS:")
        print(f"   Initial Capital:       ${self.initial_capital:,.2f}")
        print(f"   Final Equity:          ${self.final_equity:,.2f}")
        print(f"   Net P&L:               ${self.final_equity - self.initial_capital:,.2f}")
        print(f"   ROI ({self.backtest_days} days):     {metrics['roi']:.2f}%")
        print(f"   ROI (30 days proj):    {metrics['roi_monthly']:.2f}%")
        print(f"   Max Drawdown:          {metrics['max_drawdown']:.2f}%")
        print(f"   Sharpe Ratio:          {metrics['sharpe_ratio']:.2f}")
        
        # Position Details
        print(f"\n💼 POSITIONS:")
        print(f"   Spot BTC:              {self.final_state['spot_qty']:.6f}")
        print(f"   Futures Short:         {self.final_state['futures_short_qty']:.6f}")
        print(f"   Futures Margin:        ${self.final_state['futures_margin']:.2f}")
        print(f"   Cash Balance:          ${self.final_state['balance']:.2f}")
        print(f"   Center Price:          ${self.final_state['center_price']:.2f}")
        
        # Grid Trading
        print(f"\n📈 GRID TRADING:")
        print(f"   Buy Orders:            {metrics['grid_buys']}")
        print(f"   Sell Orders:           {metrics['grid_sells']}")
        print(f"   Win Rate:              {metrics['win_rate']:.1f}%")
        print(f"   Grid Profit:           ${metrics['grid_profit']:.2f}")
        print(f"   Avg per Trade:         ${metrics['grid_profit']/max(metrics['grid_sells'],1):.2f}")
        
        # Hedge Trading
        print(f"\n🛡️  HEDGE TRADING:")
        print(f"   Hedge Opens:           {metrics['hedge_opens']}")
        print(f"   Hedge Closes:          {metrics['hedge_closes']}")
        print(f"   Hedge P&L:             ${metrics['hedge_pnl']:.2f}")
        print(f"   Active Layers:         {self.final_state['hedge_layers']}")
        
        # Costs
        print(f"\n💸 COSTS:")
        print(f"   Spot Fees:             ${self.equity_curve['total_fees'].iloc[-1] if len(self.equity_curve) > 0 else 0:.2f}")
        print(f"   Funding Paid:          ${metrics['total_funding']:.2f}")
        print(f"   Total Costs:           ${metrics['total_fees'] + metrics['total_funding']:.2f}")
        print(f"   Cost as % of Capital:  {(metrics['total_fees'] + metrics['total_funding'])/self.initial_capital*100:.2f}%")
        
        # Analysis
        print(f"\n📊 ANALYSIS:")
        gross_profit = metrics['grid_profit'] + metrics['hedge_pnl']
        net_profit = self.final_equity - self.initial_capital
        print(f"   Gross Profit:          ${gross_profit:.2f}")
        print(f"   Costs:                 ${metrics['total_fees'] + metrics['total_funding']:.2f}")
        print(f"   Net Profit:            ${net_profit:.2f}")
        
        # Target Check
        target_roi = 13.0
        print(f"\n🎯 TARGET CHECK:")
        print(f"   Target ROI/month:      {target_roi}%")
        print(f"   Actual ROI/month:      {metrics['roi_monthly']:.2f}%")
        if metrics['roi_monthly'] >= target_roi:
            print(f"   Status:                ✅ TARGET ACHIEVED!")
        else:
            gap = target_roi - metrics['roi_monthly']
            print(f"   Status:                ⚠️  Short by {gap:.2f}%")
        
        print("="*70 + "\n")
    
    def plot_results(self):
        """Generate comprehensive charts with candlestick and entry points"""
        if self.equity_curve.empty:
            print("No data to plot")
            return
        
        try:
            # Create main performance charts
            self._plot_performance_charts()
            
            # Create candlestick charts with entry points
            self._plot_candlestick_with_entries()
            
        except Exception as e:
            print(f"❌ Error plotting: {e}")
            import traceback
            traceback.print_exc()
    
    def _plot_performance_charts(self):
        """Plot performance overview charts"""
        fig = plt.figure(figsize=(16, 12))
        gs = fig.add_gridspec(4, 2, hspace=0.3, wspace=0.3)
        
        # 1. Equity Curve
        ax1 = fig.add_subplot(gs[0, :])
        ax1.plot(self.equity_curve['timestamp'], self.equity_curve['equity'], 
                label='Total Equity', linewidth=2, color='blue')
        ax1.axhline(y=self.initial_capital, color='gray', linestyle='--', 
                   label='Initial Capital', alpha=0.7)
        ax1.set_title('Equity Curve', fontsize=14, fontweight='bold')
        ax1.set_ylabel('Equity ($)')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 2. Price & EMA
        ax2 = fig.add_subplot(gs[1, :])
        ax2.plot(self.equity_curve['timestamp'], self.equity_curve['price'], 
                label='BTC Price', linewidth=1.5, color='orange')
        ax2.plot(self.equity_curve['timestamp'], self.equity_curve['ema'], 
                label='EMA50 (Grid Center)', linewidth=1.5, color='purple', linestyle='--')
        ax2.set_title('Price & Grid Center', fontsize=14, fontweight='bold')
        ax2.set_ylabel('Price ($)')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # 3. Spot & Futures Positions
        ax3 = fig.add_subplot(gs[2, 0])
        ax3.plot(self.equity_curve['timestamp'], self.equity_curve['spot_value'], 
                label='Spot Value', linewidth=2, color='green')
        ax3.plot(self.equity_curve['timestamp'], self.equity_curve['balance'], 
                label='Cash', linewidth=2, color='blue')
        ax3.set_title('Spot Position & Cash', fontsize=12, fontweight='bold')
        ax3.set_ylabel('Value ($)')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # 4. Futures Position
        ax4 = fig.add_subplot(gs[2, 1])
        ax4.plot(self.equity_curve['timestamp'], self.equity_curve['futures_short_qty'], 
                label='Short Qty', linewidth=2, color='red')
        ax4.set_title('Futures Short Position', fontsize=12, fontweight='bold')
        ax4.set_ylabel('BTC')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        
        # 5. PnL Breakdown
        ax5 = fig.add_subplot(gs[3, 0])
        ax5.plot(self.equity_curve['timestamp'], self.equity_curve['spot_pnl'], 
                label='Spot PnL', linewidth=1.5, color='green')
        ax5.plot(self.equity_curve['timestamp'], self.equity_curve['futures_pnl'], 
                label='Futures PnL', linewidth=1.5, color='red')
        ax5.axhline(y=0, color='gray', linestyle='--', alpha=0.5)
        ax5.set_title('Unrealized PnL', fontsize=12, fontweight='bold')
        ax5.set_ylabel('PnL ($)')
        ax5.legend()
        ax5.grid(True, alpha=0.3)
        
        # 6. Cumulative Costs
        ax6 = fig.add_subplot(gs[3, 1])
        ax6.plot(self.equity_curve['timestamp'], self.equity_curve['total_fees'], 
                label='Trading Fees', linewidth=1.5, color='orange')
        ax6.plot(self.equity_curve['timestamp'], self.equity_curve['funding_paid'], 
                label='Funding Paid', linewidth=1.5, color='purple')
        ax6.set_title('Cumulative Costs', fontsize=12, fontweight='bold')
        ax6.set_ylabel('Cost ($)')
        ax6.legend()
        ax6.grid(True, alpha=0.3)
        
        plt.savefig('backtest_results_v2.png', dpi=150, bbox_inches='tight')
        print("[CHART] Performance charts saved to: backtest_results_v2.png")
    
    def _plot_candlestick_with_entries(self):
        """Plot candlestick chart with trade entry/exit points"""
        # Get OHLC data from equity curve
        if 'open' not in self.equity_curve.columns:
            # If no OHLC, create from close prices
            self.equity_curve['open'] = self.equity_curve['price']
            self.equity_curve['high'] = self.equity_curve['price']
            self.equity_curve['low'] = self.equity_curve['price']
            self.equity_curve['close'] = self.equity_curve['price']
        
        # Create figure with 2 subplots
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(20, 14), 
                                        gridspec_kw={'height_ratios': [3, 1]})
        
        # Plot 1: Candlestick with grid trades
        self._plot_candlestick(ax1, 'Grid Trading Entries/Exits')
        
        # Add grid buy/sell markers
        grid_buys = self.trades[self.trades['type'] == 'GRID_BUY'].copy()
        grid_sells = self.trades[self.trades['type'] == 'GRID_SELL'].copy()
        
        # Use 'price' for BUY, 'exit_price' for SELL
        if not grid_buys.empty:
            ax1.scatter(grid_buys['timestamp'], grid_buys['price'], 
                       color='lime', marker='^', s=250, alpha=0.9, 
                       label=f'Grid BUY ({len(grid_buys)})', zorder=10, 
                       edgecolors='darkgreen', linewidth=2.5)
        
        if not grid_sells.empty:
            ax1.scatter(grid_sells['timestamp'], grid_sells['exit_price'], 
                       color='red', marker='v', s=250, alpha=0.9, 
                       label=f'Grid SELL ({len(grid_sells)})', zorder=10, 
                       edgecolors='darkred', linewidth=2.5)
        
        # Add EMA line
        ax1.plot(self.equity_curve['timestamp'], self.equity_curve['ema'], 
                color='purple', linewidth=2, label='EMA50 (Grid Center)', 
                linestyle='--', alpha=0.7)
        
        ax1.legend(loc='upper left', fontsize=11)
        
        # Plot 2: Hedge positions
        self._plot_candlestick(ax2, 'Hedge Entries/Exits')
        
        # Add hedge markers
        hedge_opens = self.trades[self.trades['type'] == 'HEDGE_OPEN'].copy()
        hedge_closes = self.trades[self.trades['type'] == 'HEDGE_CLOSE_ALL'].copy()
        
        if not hedge_opens.empty:
            ax2.scatter(hedge_opens['timestamp'], hedge_opens['price'], 
                       color='orange', marker='s', s=250, alpha=0.9, 
                       label=f'Hedge OPEN ({len(hedge_opens)})', zorder=10, 
                       edgecolors='darkorange', linewidth=2.5)
        
        if not hedge_closes.empty:
            # Use exit_price for hedge closes
            ax2.scatter(hedge_closes['timestamp'], hedge_closes['exit_price'], 
                       color='cyan', marker='D', s=250, alpha=0.9, 
                       label=f'Hedge CLOSE ({len(hedge_closes)})', zorder=10, 
                       edgecolors='darkblue', linewidth=2.5)
        
        # Add EMA line
        ax2.plot(self.equity_curve['timestamp'], self.equity_curve['ema'], 
                color='purple', linewidth=2, label='EMA50', 
                linestyle='--', alpha=0.7)
        
        ax2.legend(loc='upper left', fontsize=11)
        
        plt.tight_layout()
        plt.savefig('entry_points_ohlc.png', dpi=150, bbox_inches='tight')
        print("[CHART] Candlestick with entry points saved to: entry_points_ohlc.png")
    
    def _plot_candlestick(self, ax, title):
        """Helper to plot candlestick chart"""
        df = self.equity_curve.copy()
        
        # Ensure we have OHLC columns
        if 'open' not in df.columns:
            df['open'] = df['price']
            df['high'] = df['price']
            df['low'] = df['price']
            df['close'] = df['price']
        
        # Plot candlesticks
        for idx, row in df.iterrows():
            timestamp = row['timestamp']
            open_price = row['open']
            high_price = row['high']
            low_price = row['low']
            close_price = row['close']
            
            # Determine color
            color = 'green' if close_price >= open_price else 'red'
            alpha = 0.6
            
            # Draw high-low line
            ax.plot([timestamp, timestamp], [low_price, high_price], 
                   color=color, linewidth=1, alpha=alpha)
            
            # Draw body rectangle
            body_height = abs(close_price - open_price)
            body_bottom = min(open_price, close_price)
            
            # Width in time units (adjust based on data frequency)
            if len(df) > 1:
                time_diff = (df['timestamp'].iloc[1] - df['timestamp'].iloc[0]).total_seconds() / 3600
                width = pd.Timedelta(hours=time_diff * 0.6)
            else:
                width = pd.Timedelta(hours=0.5)
            
            rect = Rectangle((timestamp - width/2, body_bottom), 
                           width, body_height,
                           facecolor=color, edgecolor=color, 
                           alpha=alpha, linewidth=0.5)
            ax.add_patch(rect)
        
        # Format
        ax.set_title(title, fontsize=14, fontweight='bold', pad=15)
        ax.set_ylabel('Price ($)', fontsize=12)
        ax.grid(True, alpha=0.3, linestyle='--')
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H:%M'))
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
        
        # Set y-axis limits with padding
        price_min = df[['open', 'high', 'low', 'close']].min().min()
        price_max = df[['open', 'high', 'low', 'close']].max().max()
        price_range = price_max - price_min
        ax.set_ylim(price_min - price_range * 0.05, price_max + price_range * 0.05)
