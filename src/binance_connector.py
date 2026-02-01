"""
Binance Live Trading Connector
"""
from binance.client import Client
from binance.exceptions import BinanceAPIException
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import time

class BinanceTradingBot:
    """Live trading bot for Binance"""
    
    def __init__(self, api_key: str, api_secret: str, testnet: bool = True):
        """
        Initialize Binance client
        
        Args:
            api_key: Binance API key
            api_secret: Binance API secret
            testnet: Use testnet (True) or live (False)
        """
        self.testnet = testnet
        
        if testnet:
            # Testnet client with timestamp sync
            self.client = Client(api_key, api_secret, testnet=True)
            self.client.API_URL = 'https://testnet.binance.vision/api'
            # Sync timestamp with server
            self.client.timestamp_offset = self._get_timestamp_offset()
            print("✅ Connected to Binance TESTNET")
        else:
            # Live client
            self.client = Client(api_key, api_secret)
            print("⚠️ Connected to Binance LIVE TRADING")
        
        self.positions = {}
        self.orders = []
    
    def _get_timestamp_offset(self) -> int:
        """Calculate timestamp offset between local and server"""
        try:
            server_time = self.client.get_server_time()
            local_time = int(time.time() * 1000)
            offset = server_time['serverTime'] - local_time
            print(f"⏰ Timestamp offset: {offset}ms")
            return offset
        except:
            return 0
        
    def test_connection(self) -> bool:
        """Test API connection"""
        try:
            status = self.client.get_system_status()
            account = self.client.get_account()
            
            print(f"\n{'='*70}")
            print("BINANCE CONNECTION TEST")
            print(f"{'='*70}")
            print(f"Status: {status['msg']}")
            print(f"Mode: {'TESTNET' if self.testnet else 'LIVE TRADING'}")
            print(f"Can Trade: {account['canTrade']}")
            print(f"Can Withdraw: {account['canWithdraw']}")
            print(f"Can Deposit: {account['canDeposit']}")
            
            # Get balances
            balances = {b['asset']: float(b['free']) 
                       for b in account['balances'] 
                       if float(b['free']) > 0}
            
            print(f"\n💰 Account Balances:")
            for asset, amount in balances.items():
                print(f"  {asset}: {amount:,.8f}")
            
            return True
            
        except BinanceAPIException as e:
            print(f"❌ Connection failed: {e}")
            return False
    
    def get_price(self, symbol: str) -> float:
        """Get current price for symbol"""
        try:
            ticker = self.client.get_symbol_ticker(symbol=symbol)
            return float(ticker['price'])
        except BinanceAPIException as e:
            print(f"❌ Error getting price for {symbol}: {e}")
            return 0.0
    
    def get_account_balance(self, asset: str = 'USDT') -> float:
        """Get balance for specific asset"""
        try:
            balance = self.client.get_asset_balance(asset=asset)
            return float(balance['free'])
        except BinanceAPIException as e:
            print(f"❌ Error getting balance: {e}")
            return 0.0
    
    def get_historical_data(self, symbol: str, interval: str = '1h', 
                           days: int = 30) -> pd.DataFrame:
        """
        Download historical klines
        
        Args:
            symbol: Trading pair (e.g., 'BTCUSDT')
            interval: Kline interval ('1m', '5m', '1h', '1d')
            days: Number of days to download
        """
        try:
            # Calculate start time
            start_time = datetime.now() - timedelta(days=days)
            start_str = start_time.strftime('%Y-%m-%d')
            
            print(f"Downloading {symbol} {interval} data from {start_str}...")
            
            # Get klines
            klines = self.client.get_historical_klines(
                symbol, interval, start_str
            )
            
            # Convert to DataFrame
            df = pd.DataFrame(klines, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_volume', 'trades', 
                'taker_buy_base', 'taker_buy_quote', 'ignore'
            ])
            
            # Convert to proper types
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df = df.set_index('timestamp')
            
            for col in ['open', 'high', 'low', 'close', 'volume']:
                df[col] = df[col].astype(float)
            
            # Keep only needed columns
            df = df[['open', 'high', 'low', 'close', 'volume']]
            
            print(f"✅ Downloaded {len(df)} bars")
            return df
            
        except BinanceAPIException as e:
            print(f"❌ Error downloading data: {e}")
            return pd.DataFrame()
    
    def get_latest_candles(self, symbol: str, interval: str = '1h', limit: int = 100) -> List[Dict]:
        """Get latest candles for chart"""
        try:
            klines = self.client.get_klines(symbol=symbol, interval=interval, limit=limit)
            candles = []
            for k in klines:
                # k[0] is open time in ms
                candles.append({
                    'time': int(k[0] / 1000), # Unix seconds
                    'open': float(k[1]),
                    'high': float(k[2]),
                    'low': float(k[3]),
                    'close': float(k[4])
                })
            return candles
        except BinanceAPIException as e:
            print(f"❌ Error getting candles: {e}")
            return []

    def place_market_order(self, symbol: str, side: str, quantity: float) -> Dict:
        """
        Place market order
        
        Args:
            symbol: Trading pair
            side: 'BUY' or 'SELL'
            quantity: Amount to trade
        """
        try:
            print(f"\n📝 Placing {side} order: {quantity} {symbol}")
            
            order = self.client.create_order(
                symbol=symbol,
                side=side,
                type='MARKET',
                quantity=quantity
            )
            
            print(f"✅ Order placed: {order['orderId']}")
            print(f"Status: {order['status']}")
            print(f"Executed Qty: {order['executedQty']}")
            
            self.orders.append(order)
            return order
            
        except BinanceAPIException as e:
            print(f"❌ Order failed: {e}")
            return {}
    
    def place_limit_order(self, symbol: str, side: str, 
                         quantity: float, price: float) -> Dict:
        """
        Place limit order
        
        Args:
            symbol: Trading pair
            side: 'BUY' or 'SELL'
            quantity: Amount to trade
            price: Limit price
        """
        try:
            print(f"\n📝 Placing {side} limit order: {quantity} {symbol} @ {price}")
            
            order = self.client.create_order(
                symbol=symbol,
                side=side,
                type='LIMIT',
                timeInForce='GTC',
                quantity=quantity,
                price=price
            )
            
            print(f"✅ Limit order placed: {order['orderId']}")
            self.orders.append(order)
            return order
            
        except BinanceAPIException as e:
            print(f"❌ Order failed: {e}")
            return {}
    
    def get_open_orders(self, symbol: Optional[str] = None) -> List[Dict]:
        """Get all open orders"""
        try:
            if symbol:
                orders = self.client.get_open_orders(symbol=symbol)
            else:
                orders = self.client.get_open_orders()
            
            return orders
            
        except BinanceAPIException as e:
            print(f"❌ Error getting orders: {e}")
            return []
    
    def cancel_order(self, symbol: str, order_id: int) -> bool:
        """Cancel an order"""
        try:
            result = self.client.cancel_order(symbol=symbol, orderId=order_id)
            print(f"✅ Order {order_id} cancelled")
            return True
            
        except BinanceAPIException as e:
            print(f"❌ Cancel failed: {e}")
            return False
    
    def get_order_status(self, symbol: str, order_id: int) -> Dict:
        """Check order status"""
        try:
            order = self.client.get_order(symbol=symbol, orderId=order_id)
            return order
        except BinanceAPIException as e:
            print(f"❌ Error checking order: {e}")
            return {}
    
    def get_recent_trades(self, symbol: str, limit: int = 50) -> List[Dict]:
        """Get recent trades for symbol"""
        try:
            return self.client.get_my_trades(symbol=symbol, limit=limit)
        except BinanceAPIException as e:
            print(f"❌ Error getting trades: {e}")
            return []

    def get_account_info(self) -> Dict:
        """Get full account information"""
        try:
            return self.client.get_account()
        except BinanceAPIException as e:
            print(f"❌ Error getting account info: {e}")
            return {}
