"""
Data loading and generation utilities
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def load_csv_data(filepath):
    """Load data from CSV file"""
    try:
        data = pd.read_csv(filepath)
        data['timestamp'] = pd.to_datetime(data['timestamp'])
        return data
    except Exception as e:
        print(f"Error loading {filepath}: {e}")
        return None

def download_btc_data(start_date, end_date):
    """Download BTC data from Yahoo Finance"""
    try:
        import yfinance as yf
        
        print(f"Downloading BTC-USD from {start_date} to {end_date}...")
        ticker = yf.Ticker("BTC-USD")
        df = ticker.history(start=start_date, end=end_date, interval='1h')
        
        if df.empty:
            print("No hourly data, trying daily...")
            df = ticker.history(start=start_date, end=end_date, interval='1d')
            if not df.empty:
                df = df.resample('1H').interpolate(method='linear')
        
        df = df.rename(columns={
            'Open': 'open', 'High': 'high',
            'Low': 'low', 'Close': 'close',
            'Volume': 'volume'
        })
        
        df = df.reset_index()
        df = df.rename(columns={'index': 'timestamp', 'Datetime': 'timestamp'})
        df = df[['timestamp', 'open', 'high', 'low', 'close', 'volume']]
        
        print(f"Downloaded {len(df)} bars")
        return df
        
    except Exception as e:
        print(f"Error: {e}")
        return None

def generate_crash_data(start_price, end_price, days, scenario='gradual'):
    """Generate simulated crash data"""
    hours = days * 24
    timestamps = [datetime(2022, 1, 1) + timedelta(hours=i) for i in range(hours)]
    total_change = (end_price - start_price) / start_price
    
    prices = []
    for i in range(hours):
        progress = i / hours
        
        if scenario == 'gradual':
            base_price = start_price + (total_change * start_price * progress)
            noise = np.random.normal(0, base_price * 0.01)
        elif scenario == 'steep':
            crash_hours = int(hours * 0.3)
            if i < crash_hours:
                base_price = start_price + (total_change * 0.7 * start_price * (i / crash_hours))
                noise = np.random.normal(0, base_price * 0.02)
            else:
                remaining = total_change * 0.3
                base_price = start_price + (total_change * 0.7 * start_price) + (remaining * start_price * ((i - crash_hours) / (hours - crash_hours)))
                noise = np.random.normal(0, base_price * 0.01)
        else:  # volatile
            base_price = start_price + (total_change * start_price * progress)
            swing = np.sin(i / 72 * 2 * np.pi) * base_price * 0.05
            noise = np.random.normal(0, base_price * 0.02)
            base_price += swing
        
        prices.append(max(base_price + noise, end_price * 0.9))
    
    data = []
    for i, timestamp in enumerate(timestamps):
        close = prices[i]
        volatility = close * 0.005
        high = close + abs(np.random.normal(0, volatility))
        low = close - abs(np.random.normal(0, volatility))
        open_price = (high + low) / 2 + np.random.normal(0, volatility/2)
        high = max(high, open_price, close)
        low = min(low, open_price, close)
        volume = np.random.uniform(1000, 10000)
        
        data.append({
            'timestamp': timestamp,
            'open': open_price,
            'high': high,
            'low': low,
            'close': close,
            'volume': volume
        })
    
    return pd.DataFrame(data)
