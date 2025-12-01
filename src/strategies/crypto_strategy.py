import re
from strategy import BaseStrategy
from data_feed import DataFeed
from analytics import ProbabilityEngine
from risk_manager import RiskManager

class CryptoPriceStrategy(BaseStrategy):
    """
    Strategy for "Price > X" markets.
    """
    def __init__(self, client, min_confidence=0.7):
        super().__init__(client)
        self.data_feed = DataFeed()
        self.risk_manager = RiskManager()
        self.min_confidence = min_confidence
        self.volatility_map = {
            "BTC": 0.6, # 60% annualized volatility
            "ETH": 0.7,
            "SOL": 0.8
        }

    def parse_market(self, title, slug):
        """
        Extract asset, strike price, and direction from market title/slug.
        Example: "Bitcoin above 100k by 2024"
        """
        title_lower = title.lower()
        
        # Detect Asset
        asset = None
        if "bitcoin" in title_lower or "btc" in title_lower:
            asset = "BTC"
        elif "ethereum" in title_lower or "eth" in title_lower:
            asset = "ETH"
        elif "solana" in title_lower or "sol" in title_lower:
            asset = "SOL"
            
        if not asset:
            return None

        # Detect Strike Price (Simplified regex)
        # Looking for "$100,000", "100k", "50000"
        # This is tricky and requires robust regex.
        # Let's try to find numbers near "above" or ">"
        
        strike = None
        # Regex for "above $X" or "above X"
        match = re.search(r'above\s+\$?([\d,]+)(k?)', title_lower)
        if match:
            num_str = match.group(1).replace(",", "")
            multiplier = 1000 if match.group(2) == 'k' else 1
            try:
                strike = float(num_str) * multiplier
            except:
                pass
                
        if not strike:
            return None
            
        return {
            "asset": asset,
            "strike": strike,
            "direction": "ABOVE" # Assuming "above" markets for now
        }

    def run(self):
        print(f"[{self.__class__.__name__}] Scanning for Crypto opportunities...")
        try:
            markets = self.client.get_active_markets(limit=50)
            
            for item in markets:
                # Assuming item has 'title' and 'deadline'
                # If not, we might need to fetch details.
                # Let's assume the list endpoint returns basic metadata.
                
                # Note: The actual API response structure needs to be verified.
                # If 'title' is missing, we skip.
                if 'title' not in item or 'slug' not in item:
                    continue

                parsed = self.parse_market(item['title'], item['slug'])
                if not parsed:
                    continue
                    
                print(f"  Found candidate: {item['title']} -> {parsed}")
                
                # Get Real-time Price
                current_price = self.data_feed.get_crypto_price(parsed['asset'])
                if not current_price:
                    continue
                    
                # Calculate True Probability
                time_to_expiry = ProbabilityEngine.get_time_to_expiry(item.get('deadline', ''))
                volatility = self.volatility_map.get(parsed['asset'], 0.6)
                
                true_prob = ProbabilityEngine.calculate_probability(
                    current_price, 
                    parsed['strike'], 
                    time_to_expiry, 
                    volatility
                )
                
                print(f"    Current {parsed['asset']}: ${current_price}")
                print(f"    True Probability (Model): {true_prob:.4f}")
                
                # Get Market Price
                # Optimization: Only fetch orderbook if model shows promise
                # e.g. if True Prob is > 80% or < 20%
                
                if true_prob < 0.2 or true_prob > 0.8:
                    orderbook = self.client.get_orderbook(item['slug'])
                    if not orderbook:
                        continue
                        
                    # Check for mispricing
                    # If True Prob is 90%, and Market Price (YES) is 70c -> BUY YES
                    # If True Prob is 10%, and Market Price (NO) is 70c -> BUY NO (which is SELL YES or BUY NO token)
                    
                    best_ask_yes = float(orderbook['asks'][0]['price']) if orderbook['asks'] else 1.0
                    market_prob = best_ask_yes
                    
                    print(f"    Market Price (YES): {market_prob:.4f}")
                    
                    # Signal Generation
                    confidence = 0.0
                    side = -1 # 0 BUY YES, 1 BUY NO (SELL YES)
                    
                    if true_prob > market_prob + 0.10: # 10% edge
                        confidence = true_prob - market_prob
                        side = 0 # BUY YES
                        print(f"    >>> SIGNAL: BUY YES (Edge: {confidence:.2f})")
                        
                    elif true_prob < market_prob - 0.10:
                        confidence = market_prob - true_prob
                        side = 1 # SELL YES / BUY NO
                        print(f"    >>> SIGNAL: BUY NO (Edge: {confidence:.2f})")
                        
                    if confidence > 0.15: # High confidence threshold
                        # Calculate Position Size
                        # Mock portfolio balance for now (e.g. $1000)
                        portfolio_balance = 1000.0 
                        
                        # Odds = 1 / Market Price
                        odds = 1.0 / market_prob if market_prob > 0 else 1.0
                        
                        amount = self.risk_manager.calculate_position_size(portfolio_balance, true_prob, odds)
                        
                        # Apply timing risk adjustment
                        timing_multiplier = self.risk_manager.check_timing_risk(time_to_expiry)
                        amount *= timing_multiplier
                        
                        if amount > 1.0: # Minimum trade size $1
                            print(f"    >>> SIGNAL: { 'BUY YES' if side == 0 else 'BUY NO' } (Edge: {confidence:.2f})")
                            print(f"    [RISK] Position Size: ${amount:.2f} (Kelly: {self.risk_manager.kelly_fraction})")
                            
                            # Execute Trade (Uncomment to enable)
                            # token_id = item['tokens']['yes'] if side == 0 else item['tokens']['no']
                            # price_cents = int(market_prob * 100) + (1 if side == 0 else -1)
                            # self.client.create_order(item['slug'], token_id, 0, price_cents, amount)
                        else:
                            print(f"    [RISK] Signal ignored (Size too small: ${amount:.2f})")

        except Exception as e:
            print(f"Error in CryptoStrategy: {e}")
