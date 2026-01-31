from configs.strategy_configs import CONFIGS
from core.strategy import DynamicGridHedgeStrategy
from core.backtest import BacktestEngine
from core.performance import PerformanceAnalyzer
from utils.data_loader import download_btc_data
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

print('Testing with 6 months recent BTC data...\n')

# Calculate dates (6 months from now)
end_date = datetime.now()
start_date = end_date - timedelta(days=180)

print(f'Period: {start_date.strftime("%Y-%m-%d")} to {end_date.strftime("%Y-%m-%d")}')
print('Downloading BTC data from Yahoo Finance...\n')

# Download data
data = download_btc_data(start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))

if data is None or data.empty:
    print('ERROR: Failed to download data!')
    exit(1)

print(f'Data loaded: {len(data)} bars')
print(f'Price range: ${data["close"].min():.2f} - ${data["close"].max():.2f}')
print(f'Start price: ${data["close"].iloc[0]:.2f}')
print(f'End price: ${data["close"].iloc[-1]:.2f}')
price_change = ((data["close"].iloc[-1] - data["close"].iloc[0]) / data["close"].iloc[0]) * 100
print(f'Price change: {price_change:+.2f}%\n')

# Test with ADAPTIVE config
config = CONFIGS['adaptive'].copy()
config['backtest_days'] = 180

# Prepare data
data_indexed = data.set_index('timestamp')

print('Running backtest with ADAPTIVE config...')
strategy = DynamicGridHedgeStrategy(config)
engine = BacktestEngine(strategy, data_indexed, config)
results = engine.run()

print('\nAnalyzing results...')
analyzer = PerformanceAnalyzer(results, config)
metrics = analyzer.calculate_metrics()

print('\n' + '='*70)
print('RESULTS - 6 MONTHS RECENT BTC DATA')
print('='*70)
print(f'Config:           ADAPTIVE')
print(f'Period:           {start_date.strftime("%Y-%m-%d")} to {end_date.strftime("%Y-%m-%d")}')
print(f'Price:            ${data["close"].iloc[0]:.2f} -> ${data["close"].iloc[-1]:.2f} ({price_change:+.2f}%)')
print(f'\nROI:              {metrics["roi"]:+.2f}%')
print(f'Max Drawdown:     {metrics["max_drawdown"]:.2f}%')
print(f'Sharpe Ratio:     {metrics["sharpe_ratio"]:.2f}')
print(f'Win Rate:         {metrics["win_rate"]:.1f}%')
print(f'\nGrid Trades:      {metrics["grid_buys"]} buys, {metrics["grid_sells"]} sells')
print(f'Grid Profit:      ${metrics["grid_profit"]:.2f}')
print(f'Hedge Trades:     {metrics["hedge_opens"]} opens, {metrics["hedge_closes"]} closes')
print(f'Hedge Profit:     ${metrics["hedge_pnl"]:.2f}')
print(f'\nTotal Fees:       ${metrics["total_fees"]:.2f}')
print('='*70)

print('\nGenerating candlestick charts...')
analyzer.plot_results()

print('\nTest complete!')
print('\nFiles created:')
print('  - backtest_results_v2.png (Performance overview)')
print('  - entry_points_ohlc.png (Candlestick with all entry/exit points)')
print('\nOpen entry_points_ohlc.png to see:')
print('  Chart 1: Grid BUY/SELL markers on OHLC candlesticks')
print('  Chart 2: Hedge OPEN/CLOSE markers')
