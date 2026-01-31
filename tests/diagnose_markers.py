from configs.strategy_configs import CONFIGS
from core.strategy import DynamicGridHedgeStrategy
from core.backtest import BacktestEngine
from core.performance import PerformanceAnalyzer
from utils.data_loader import download_btc_data
from datetime import datetime, timedelta
import pandas as pd

print('Checking 6-month data for marker visibility issues...\n')

# Load the same 6-month data
end_date = datetime.now()
start_date = end_date - timedelta(days=180)

print('Loading data...')
data = download_btc_data(start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
data_indexed = data.set_index('timestamp')

config = CONFIGS['adaptive'].copy()
config['backtest_days'] = 180

strategy = DynamicGridHedgeStrategy(config)
engine = BacktestEngine(strategy, data_indexed, config)
results = engine.run()

# Analyze trades distribution
trades = results['trades']
print(f'\n=== TRADES BREAKDOWN ===')
print(f'Total trades: {len(trades)}')
print(f'\nBy type:')
for trade_type in ['GRID_BUY', 'GRID_SELL', 'HEDGE_OPEN', 'HEDGE_CLOSE_ALL']:
    count = len(trades[trades['type'] == trade_type])
    print(f'  {trade_type:20} {count:3} trades')

# Check if trades have valid timestamps and prices
grid_sells = trades[trades['type'] == 'GRID_SELL']
hedge_closes = trades[trades['type'] == 'HEDGE_CLOSE_ALL']

print(f'\n=== GRID SELL DETAILS ===')
if not grid_sells.empty:
    print(f'Count: {len(grid_sells)}')
    print(f'Price range: ${grid_sells["price"].min():.2f} - ${grid_sells["price"].max():.2f}')
    print(f'First 3 sells:')
    print(grid_sells[['timestamp', 'price', 'qty']].head(3).to_string(index=False))
else:
    print('NO GRID SELLS FOUND!')

print(f'\n=== HEDGE CLOSE DETAILS ===')
if not hedge_closes.empty:
    print(f'Count: {len(hedge_closes)}')
    print(f'Price range: ${hedge_closes["price"].min():.2f} - ${hedge_closes["price"].max():.2f}')
    print(f'First 3 closes:')
    print(hedge_closes[['timestamp', 'price']].head(3).to_string(index=False))
else:
    print('NO HEDGE CLOSES FOUND!')

print(f'\n=== DIAGNOSIS ===')
if grid_sells.empty:
    print('PROBLEM: No Grid SELL trades recorded!')
    print('  → Red triangles cannot be shown (no data)')
else:
    print(f'Grid SELL OK: {len(grid_sells)} trades exist')
    print('  → Red triangles SHOULD be visible on chart')

if hedge_closes.empty:
    print('PROBLEM: No Hedge CLOSE trades recorded!')
    print('  → Cyan diamonds cannot be shown (no data)')
else:
    print(f'Hedge CLOSE OK: {len(hedge_closes)} trades exist')
    print('  → Cyan diamonds SHOULD be visible on chart')

print('\nRecommendation:')
print('  • If trades exist but not visible: Markers may be too small for 4000+ bars')
print('  • Solution: Create zoomed charts for specific periods')
print('  • Or: Use interactive mode to filter date ranges')
