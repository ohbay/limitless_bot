from abc import ABC, abstractmethod
import random
import time

class BaseStrategy(ABC):
    def __init__(self, client):
        self.client = client

    @abstractmethod
    def run(self):
        """Main execution logic for the strategy."""
        pass

class SimpleStrategy(BaseStrategy):
    """
    A simple strategy that looks for markets with specific probability ranges
    and places small orders if the spread is favorable.
    """
    def __init__(self, client, min_prob=40, max_prob=60, max_spend_usdc=1.0):
        super().__init__(client)
        self.min_prob = min_prob
        self.max_prob = max_prob
        self.max_spend_usdc = max_spend_usdc

    def run(self):
        print(f"[{self.__class__.__name__}] Scanning markets...")
        try:
            markets = self.client.get_active_markets(limit=50)
            
            # The API response structure for 'markets/active' returns a list of groups/markets.
            # We need to handle the specific structure.
            # Based on docs, it returns a DTO. Let's assume it's a list or has a 'markets' key.
            # If it's a list of mixed types (groups vs single markets), we need to filter.
            
            # For safety, let's just inspect the first few items or handle errors gracefully.
            # In a real scenario, we'd strictly type this.
            
            # Simplified logic: Iterate and find a candidate
            for item in markets:
                # Handle nested markets in groups if necessary, 
                # but for now let's look for direct market objects or flat list if API returns that.
                # The docs say: "Active markets and groups".
                
                # Let's assume 'item' is a market dict for simplicity of this demo strategy.
                # We check for 'slug' and 'tokens'.
                if 'slug' not in item:
                    continue
                    
                slug = item['slug']
                
                # Fetch full details/orderbook to make a decision
                # Optimization: Don't fetch orderbook for every market, filter by basic data first if available.
                
                # For this demo, let's pick one random market to analyze to avoid rate limits
                if random.random() > 0.1: 
                    continue
                    
                print(f"Analyzing market: {slug}")
                orderbook = self.client.get_orderbook(slug)
                
                if not orderbook or 'bids' not in orderbook or 'asks' not in orderbook:
                    continue
                    
                best_bid = float(orderbook['bids'][0]['price']) if orderbook['bids'] else 0
                best_ask = float(orderbook['asks'][0]['price']) if orderbook['asks'] else 1
                
                spread = best_ask - best_bid
                mid_price = (best_ask + best_bid) / 2 * 100 # Convert to cents
                
                print(f"  > Bid: {best_bid}, Ask: {best_ask}, Spread: {spread:.4f}")
                
                # Strategy Logic:
                # If probability (mid price) is within range and spread is tight enough
                if self.min_prob <= mid_price <= self.max_prob and spread < 0.05:
                    print(f"  >>> OPPORTUNITY FOUND in {slug}!")
                    
                    # Example Action: Place a BUY order slightly better than best bid
                    # BUT for safety in this demo, we will just LOG it.
                    # Uncomment below to enable trading.
                    
                    # my_price = int(best_bid * 100) + 1 # 1 cent better
                    # token_id = item['tokens']['yes'] # Assuming structure
                    # self.client.create_order(slug, token_id, 0, my_price, 10)
                    
        except Exception as e:
            print(f"Error in strategy run: {e}")

class RandomStrategy(BaseStrategy):
    """
    A chaos strategy for testing.
    """
    def run(self):
        print("Random strategy running (doing nothing for safety).")
