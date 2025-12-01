import sys
import os
import time

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from strategies.crypto_strategy import CryptoPriceStrategy
from api_client import LimitlessClient

class MockClient(LimitlessClient):
    """Mock client to avoid hitting real API during verification."""
    def __init__(self):
        self.auth = type('obj', (object,), {'user_data': {'id': 1, 'rank': {'feeRateBps': 0}}})
        
    def get_active_markets(self, limit=100):
        # Return a fake market that looks like a Bitcoin opportunity
        return [{
            "slug": "bitcoin-above-50k-dec-2024",
            "title": "Bitcoin above $50,000 by Dec 31 2024",
            "deadline": "2024-12-31T23:59:59Z",
            "tokens": {"yes": "1", "no": "2"}
        }]

    def get_orderbook(self, slug):
        # Return a mispriced orderbook
        # True prob of BTC > 50k (if price is 90k) is ~1.0
        # We simulate market trading at 0.50 (huge opportunity)
        return {
            "bids": [{"price": "0.49", "size": "100"}],
            "asks": [{"price": "0.50", "size": "100"}]
        }
        
    def create_order(self, *args, **kwargs):
        print(f"[MockClient] Order created: {args}")
        return {"status": "success"}

def verify():
    print("Verifying Advanced Strategies...")
    
    # 1. Setup Mock Client
    client = MockClient()
    
    # 2. Setup Strategy
    strategy = CryptoPriceStrategy(client)
    
    # 3. Inject Fake Data Feed
    # We monkeypatch the data feed to return a specific price
    strategy.data_feed.get_crypto_price = lambda symbol: 95000.0 if symbol == "BTC" else 0
    
    # 4. Run Strategy
    print("\n--- Running Strategy with BTC=$95k (Target > $50k) ---")
    strategy.run()
    
    print("\nVerification Complete.")

if __name__ == "__main__":
    verify()
