from configs.strategy_configs import CONFIGS
from core.strategy import DynamicGridHedgeStrategy
from core.backtest import BacktestEngine
from core.performance import PerformanceAnalyzer
from utils.data_loader import generate_crash_data

print('Quick test - Verify all markers visible\n')

# Generate small dataset (easier to see)
data = generate_crash_data(100000, 95000, 10, 'volatile')
print(f'Generated {len(data)} bars (10 days volatile crash)\n')

config = CONFIGS['adaptive'].copy()
config['backtest_days'] = 10
data_indexed = data.set_index('timestamp')

strategy = DynamicGridHedgeStrategy(config)
engine = BacktestEngine(strategy, data_indexed, config)
results = engine.run()

analyzer = PerformanceAnalyzer(results, config)
metrics = analyzer.calculate_metrics()

# Show what we have
print('\n=== TRADE SUMMARY ===')
print(f'Grid BUY:     {metrics["grid_buys"]} trades')
print(f'Grid SELL:    {metrics["grid_sells"]} trades')
print(f'Hedge OPEN:   {metrics["hedge_opens"]} trades')
print(f'Hedge CLOSE:  {metrics["hedge_closes"]} trades')

print('\nGenerating chart...')
analyzer.plot_results()

print('\n=== MARKERS ON CHART ===')
print(f'Chart 1 should show:')
print(f'  • {metrics["grid_buys"]} LIME triangles pointing UP (Grid BUY)')
print(f'  • {metrics["grid_sells"]} RED triangles pointing DOWN (Grid SELL)')
print(f'Chart 2 should show:')
print(f'  • {metrics["hedge_opens"]} ORANGE squares (Hedge OPEN)')
print(f'  • {metrics["hedge_closes"]} CYAN diamonds (Hedge CLOSE)')
print(f'\nAll markers: 250 pixels, thick borders, z-order 10 (on top)')
print(f'\nOpen entry_points_ohlc.png to verify!')
