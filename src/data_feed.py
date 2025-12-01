import requests
import time

class DataFeed:
    """
    Fetches real-time market data from external sources (Binance).
    """
    BASE_URL = "https://api.binance.com/api/v3"

    def get_crypto_price(self, symbol="BTC"):
        """
        Get current price for a crypto asset in USDT.
        """
        # Map common symbols to Binance pairs
        symbol_map = {
            "BTC": "BTCUSDT",
            "ETH": "ETHUSDT",
            "SOL": "SOLUSDT"
        }
        
        pair = symbol_map.get(symbol.upper(), f"{symbol.upper()}USDT")
        
        try:
            url = f"{self.BASE_URL}/ticker/price?symbol={pair}"
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            data = response.json()
            return float(data['price'])
        except Exception as e:
            print(f"[DataFeed] Error fetching price for {symbol}: {e}")
            return None
