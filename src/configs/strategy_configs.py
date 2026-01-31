"""
All strategy configurations in one place
"""

# ============================================================================
# ADAPTIVE CONFIG - BEST FOR ALL CONDITIONS
# ============================================================================
CONFIG_ADAPTIVE = {
    'initial_capital': 10_000,
    
    # Grid Settings
    'grid_levels': 16,
    'grid_step': 0.016,              # 1.6%
    'grid_take_profit': 0.024,       # 2.4%
    'grid_risk_per_order': 0.048,    # 4.8%
    'rebalance_threshold': 0.095,    # 9.5%
    
    # Hedge Settings
    'hedge_atr_threshold': [4.5, 7.0, 10.0],
    'hedge_sizes': [0.06, 0.09, 0.14],
    'hedge_leverage': 2,
    
    # Indicators
    'ema_period': 50,
    'atr_period': 14,
    
    # Risk Management
    'max_drawdown': 0.29,
    'max_drawdown_threshold': 0.29,
    'margin_call_threshold': 0.35,
    'stop_loss_consecutive': 7,
}

# ============================================================================
# SCALPING CONFIG - HIGH FREQUENCY TRADING
# ============================================================================
CONFIG_SCALPING = {
    'initial_capital': 10_000,
    
    'grid_levels': 20,
    'grid_step': 0.012,              # 1.2%
    'grid_take_profit': 0.018,       # 1.8%
    'grid_risk_per_order': 0.04,     # 4%
    'rebalance_threshold': 0.08,     # 8%
    
    'hedge_atr_threshold': [5.0, 7.0, 10.0],
    'hedge_sizes': [0.05, 0.08, 0.12],
    'hedge_leverage': 2,
    
    'ema_period': 50,
    'atr_period': 14,
    
    'max_drawdown': 0.30,
    'max_drawdown_threshold': 0.30,
    'margin_call_threshold': 0.35,
    'stop_loss_consecutive': 8,
}

# ============================================================================
# CONSERVATIVE CONFIG - LOW RISK
# ============================================================================
CONFIG_CONSERVATIVE = {
    'initial_capital': 10_000,
    
    'grid_levels': 10,
    'grid_step': 0.025,              # 2.5%
    'grid_take_profit': 0.035,       # 3.5%
    'grid_risk_per_order': 0.05,     # 5%
    'rebalance_threshold': 0.18,
    
    'hedge_atr_threshold': [3.0, 4.5, 6.5],
    'hedge_sizes': [0.08, 0.12, 0.15],
    'hedge_leverage': 2,
    
    'ema_period': 24,
    'atr_period': 14,
    
    'max_drawdown': 0.15,
    'max_drawdown_threshold': 0.15,
    'margin_call_threshold': 0.40,
    'stop_loss_consecutive': 4,
}

# ============================================================================
# AGGRESSIVE CONFIG - HIGH RISK, HIGH REWARD
# ============================================================================
CONFIG_AGGRESSIVE = {
    'initial_capital': 10_000,
    
    'grid_levels': 15,
    'grid_step': 0.015,              # 1.5%
    'grid_take_profit': 0.025,       # 2.5%
    'grid_risk_per_order': 0.10,     # 10%
    'rebalance_threshold': 0.12,
    
    'hedge_atr_threshold': [2.0, 3.5, 5.5],
    'hedge_sizes': [0.12, 0.18, 0.25],
    'hedge_leverage': 3,
    
    'ema_period': 24,
    'atr_period': 14,
    
    'max_drawdown': 0.25,
    'max_drawdown_threshold': 0.25,
    'margin_call_threshold': 0.40,
    'stop_loss_consecutive': 6,
}

# ============================================================================
# CONFIG PRESETS BY MARKET CONDITION
# ============================================================================

CONFIGS = {
    'adaptive': CONFIG_ADAPTIVE,        # Best all-around
    'scalping': CONFIG_SCALPING,        # High frequency
    'conservative': CONFIG_CONSERVATIVE, # Low risk
    'aggressive': CONFIG_AGGRESSIVE,     # High risk
}

# Default config
DEFAULT_CONFIG = CONFIG_ADAPTIVE
