"""
Test Grid + Hedge strategy with 6 months recent Dow Jones (^DJI) data
"""
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from configs.strategy_configs import CONFIG_ADAPTIVE
from core.strategy import DynamicGridHedgeStrategy
from core.backtest import BacktestEngine
from core.performance import PerformanceAnalyzer

def download_dji_data(months=6):
    """Download recent Dow Jones data from Yahoo Finance"""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=months*30)
    
    print(f"\n📥 Downloading Dow Jones (^DJI) data...")
    print(f"Period: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    
    ticker = yf.Ticker("^DJI")
    df = ticker.history(start=start_date, end=end_date, interval="1h")
    
    if df.empty:
        print("⚠️ No hourly data, trying daily interval...")
        df = ticker.history(start=start_date, end=end_date, interval="1d")
    
    if df.empty:
        raise ValueError("Cannot download Dow Jones data from Yahoo Finance")
    
    # Rename columns to match our format
    df = df.rename(columns={
        'Open': 'open',
        'High': 'high', 
        'Low': 'low',
        'Close': 'close',
        'Volume': 'volume'
    })
    
    # Keep only needed columns
    df = df[['open', 'high', 'low', 'close', 'volume']].copy()
    
    print(f"✅ Downloaded {len(df)} bars")
    print(f"Date range: {df.index[0]} to {df.index[-1]}")
    print(f"Price range: {df['close'].min():.2f} - {df['close'].max():.2f}")
    
    return df

def main():
    print("="*70)
    print("DOW JONES (^DJI) 6-MONTH BACKTEST - ADAPTIVE STRATEGY")
    print("="*70)
    
    # Download data
    df = download_dji_data(months=6)
    
    # Initial price info
    initial_price = df['close'].iloc[0]
    final_price = df['close'].iloc[-1]
    price_change = ((final_price - initial_price) / initial_price) * 100
    
    print(f"\n📈 Dow Jones Movement:")
    print(f"Initial: {initial_price:,.2f}")
    print(f"Final: {final_price:,.2f}")
    print(f"Change: {price_change:+.2f}%")
    
    # Get ADAPTIVE config
    config = CONFIG_ADAPTIVE
    
    # Convert old config format to new format
    strategy_config = {
        'initial_capital': config['initial_capital'],
        'grid_step_percent': config['grid_step'] * 100,
        'take_profit_percent': config['grid_take_profit'] * 100,
        'hedge_atr_multiplier': 2.5,
        'grid_levels': config['grid_levels'],
        'grid_risk_per_order': config['grid_risk_per_order'],
        'rebalance_threshold': config['rebalance_threshold'],
        'hedge_atr_threshold': config['hedge_atr_threshold'],
        'hedge_sizes': config['hedge_sizes'],
        'hedge_leverage': config['hedge_leverage'],
        'ema_period': config['ema_period'],
        'atr_period': config['atr_period'],
        'max_drawdown': config['max_drawdown'],
    }
    
    initial_capital = strategy_config['initial_capital']
    
    print(f"\n💵 Initial Equity: ${initial_capital:,.2f}")
    print(f"\n⚙️ Strategy Config: ADAPTIVE")
    print(f"Grid Step: {strategy_config['grid_step_percent']}%")
    print(f"Take Profit: {strategy_config['take_profit_percent']}%")
    print(f"Hedge Trigger: {strategy_config['hedge_atr_multiplier']} ATR")
    
    # Run backtest
    print(f"\n{'='*70}")
    print("🚀 Running backtest...")
    print(f"{'='*70}\n")
    
    # Prepare data
    df_indexed = df.copy()
    if not isinstance(df_indexed.index, pd.DatetimeIndex):
        df_indexed = df_indexed.reset_index()
        df_indexed = df_indexed.set_index(df_indexed.columns[0])
    
    strategy = DynamicGridHedgeStrategy(config)
    engine = BacktestEngine(strategy, df_indexed, config)
    results = engine.run()
    
    # Analyze results
    analyzer = PerformanceAnalyzer(results, config)
    metrics = analyzer.calculate_metrics()
    
    # Display results with clear equity comparison
    final_capital = results['final_equity']
    profit = final_capital - initial_capital
    roi = metrics['roi']
    
    print(f"\n{'='*70}")
    print("📊 BACKTEST RESULTS")
    print(f"{'='*70}")
    
    print(f"\n💰 EQUITY COMPARISON:")
    print(f"┌{'─'*50}┐")
    print(f"│ Initial Equity:  ${initial_capital:>15,.2f}            │")
    print(f"│ Final Equity:    ${final_capital:>15,.2f}            │")
    print(f"├{'─'*50}┤")
    print(f"│ Profit/Loss:     ${profit:>15,.2f}  ({roi:>+8.2f}%) │")
    print(f"└{'─'*50}┘")
    
    print(f"\n📈 Performance Metrics:")
    print(f"ROI: {roi:+.2f}%")
    print(f"Max Drawdown: {metrics['max_drawdown']:.2f}%")
    print(f"Sharpe Ratio: {metrics['sharpe_ratio']:.2f}")
    print(f"Win Rate: {metrics['win_rate']:.1f}%")
    total_trades = metrics['grid_buys'] + metrics['grid_sells'] + metrics['hedge_opens'] + metrics['hedge_closes']
    print(f"Total Trades: {total_trades}")
    
    print(f"\n🔄 Grid Trading:")
    print(f"BUY entries: {metrics['grid_buys']}")
    print(f"SELL exits: {metrics['grid_sells']}")
    print(f"Grid Profit: ${metrics['grid_profit']:,.2f}")
    
    print(f"\n🛡️ Hedge Trading:")
    print(f"OPEN positions: {metrics['hedge_opens']}")
    print(f"CLOSE positions: {metrics['hedge_closes']}")
    if 'hedge_profit' in metrics:
        print(f"Hedge Profit: ${metrics['hedge_profit']:,.2f}")
    
    print(f"\n💸 Costs:")
    print(f"Total Fees: ${metrics['total_fees']:,.2f}")
    if 'funding_fees' in metrics:
        print(f"Funding Fees: ${metrics['funding_fees']:,.2f}")
    
    print(f"\n📊 Chart saved: entry_points_ohlc.png")
    
    # Equity summary
    print(f"\n{'='*70}")
    print("💵 FINAL EQUITY SUMMARY")
    print(f"{'='*70}")
    print(f"Started with: ${initial_capital:,.2f}")
    print(f"Ended with:   ${final_capital:,.2f}")
    print(f"Net change:   ${profit:>+,.2f} ({roi:>+.2f}%)")
    print(f"{'='*70}\n")
    
    # Interpretation
    if roi > 50:
        print("✅ EXCELLENT: ROI > 50%")
    elif roi > 20:
        print("✅ GOOD: ROI > 20%")
    elif roi > 0:
        print("⚠️ MODEST: ROI > 0% but below target")
    else:
        print("❌ LOSS: Strategy lost money in this period")
    
    if metrics['max_drawdown'] < 20:
        print("✅ SAFE: Drawdown < 20%")
    elif metrics['max_drawdown'] < 30:
        print("⚠️ MODERATE: Drawdown < 30%")
    else:
        print("❌ RISKY: Drawdown > 30%")

if __name__ == "__main__":
    main()
