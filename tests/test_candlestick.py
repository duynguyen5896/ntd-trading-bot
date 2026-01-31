from configs.strategy_configs import CONFIGS
from core.strategy import DynamicGridHedgeStrategy
from core.backtest import BacktestEngine
from core.performance import PerformanceAnalyzer
from utils.data_loader import generate_crash_data
import warnings
warnings.filterwarnings('ignore')

print('Testing Candlestick Chart Generation...\n')

# Generate test data
print('Generating crash scenario data ($60k -> $50k, 30 days)...')
data = generate_crash_data(60000, 50000, 30, 'gradual')
print(f'   Generated {len(data)} bars with OHLC data\n')

# Use ADAPTIVE config
config = CONFIGS['adaptive'].copy()
config['backtest_days'] = 30

# Prepare data
data_indexed = data.set_index('timestamp')

# Run backtest
print('Running backtest...')
strategy = DynamicGridHedgeStrategy(config)
engine = BacktestEngine(strategy, data_indexed, config)
results = engine.run()

# Analyze
print('\nAnalyzing results...')
analyzer = PerformanceAnalyzer(results, config)
metrics = analyzer.calculate_metrics()

print(f'\nResults:')
print(f'   ROI: {metrics["roi"]:+.2f}%')
print(f'   Grid Trades: {metrics["grid_buys"]} buys, {metrics["grid_sells"]} sells')
print(f'   Hedge Trades: {metrics["hedge_opens"]} opens, {metrics["hedge_closes"]} closes')

# Generate charts
print('\nGenerating charts...')
analyzer.plot_results()

print('\nTest complete!')
print('Files created:')
print('   - backtest_results_v2.png (Performance overview)')
print('   - entry_points_ohlc.png (Candlestick with entry/exit points)')
