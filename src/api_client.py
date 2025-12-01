import time
import requests
try:
    from .config import Config
    from .auth import LimitlessAuth
except ImportError:
    from config import Config
    from auth import LimitlessAuth

class LimitlessClient:
    def __init__(self):
        self.auth = LimitlessAuth()
        self.api_url = Config.API_URL
        self.session = requests.Session()
        # Initial login
        self.refresh_session()

    def refresh_session(self):
        cookie = self.auth.login()
        self.session.cookies.set("limitless_session", cookie)

    def _get_headers(self):
        return {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

    def get_active_markets(self, limit=100):
        """Retrieve active markets."""
        params = {"limit": limit, "sortBy": "newest"}
        response = self.session.get(f"{self.api_url}/markets/active", params=params)
        response.raise_for_status()
        return response.json()

    def get_market_details(self, slug):
        """Get details for a specific market."""
        response = self.session.get(f"{self.api_url}/markets/{slug}")
        response.raise_for_status()
        return response.json()

    def get_orderbook(self, slug):
        """Get orderbook for a market."""
        response = self.session.get(f"{self.api_url}/markets/{slug}/orderbook")
        if response.status_code == 404:
            return None
        response.raise_for_status()
        return response.json()

    def create_order(self, market_slug, token_id, side, price_cents, amount_shares, expiration_ts=0):
        """
        Create and submit an order.
        side: 0 for BUY, 1 for SELL
        price_cents: Limit price in cents (e.g. 50 for $0.50)
        amount_shares: Number of shares
        """
        # 1. Prepare Order Data
        user_address = self.auth.get_address()
        salt = int(time.time() * 1000) + (24 * 60 * 60 * 1000) # 24h validity for salt
        
        # Amounts calculation (USDC has 6 decimals)
        scaling_factor = 1_000_000
        price_dollars = price_cents / 100.0
        
        # Maker amount = what we give. Taker amount = what we get.
        # This logic depends on BUY vs SELL and how the contract expects it.
        # Based on docs:
        # BUY (side 0): Maker gives USDC, Taker gives Shares.
        # SELL (side 1): Maker gives Shares, Taker gives USDC.
        
        # However, the API/Contract often simplifies this to "makerAmount" and "takerAmount" 
        # relative to the asset being traded vs the quote currency.
        # Let's follow the Python example logic:
        # makerAmount = cost in USDC (if buying)
        # takerAmount = amount of shares (if buying)
        
        total_cost_usdc = price_dollars * amount_shares
        
        if side == 0: # BUY
            maker_amount = int(total_cost_usdc * scaling_factor)
            taker_amount = int(amount_shares * scaling_factor)
        else: # SELL
            # If selling, we give shares (makerAmount) and want USDC (takerAmount)
            maker_amount = int(amount_shares * scaling_factor)
            taker_amount = int(total_cost_usdc * scaling_factor)

        fee_rate_bps = self.auth.user_data.get("rank", {}).get("feeRateBps", 0)

        order_payload = {
            "salt": salt,
            "maker": user_address,
            "signer": user_address,
            "taker": "0x0000000000000000000000000000000000000000",
            "tokenId": str(token_id),
            "makerAmount": maker_amount,
            "takerAmount": taker_amount,
            "expiration": str(expiration_ts),
            "nonce": 0,
            "feeRateBps": fee_rate_bps,
            "side": side,
            "signatureType": 0, # EOA
        }

        # 2. Sign Order
        signature = self.auth.sign_order(order_payload)
        if not signature.startswith("0x"):
            signature = "0x" + signature

        # 3. Submit Order
        final_payload = {
            "order": {
                **order_payload,
                "price": price_dollars,
                "signature": signature
            },
            "ownerId": self.auth.user_data["id"],
            "orderType": "GTC",
            "marketSlug": market_slug
        }
        
        response = self.session.post(
            f"{self.api_url}/orders",
            json=final_payload,
            headers=self._get_headers()
        )
        
        if response.status_code != 201:
            print(f"Order failed: {response.text}")
            response.raise_for_status()
            
        return response.json()

    def cancel_all_orders(self, slug):
        """Cancel all orders for a market."""
        response = self.session.delete(f"{self.api_url}/orders/all/{slug}")
        response.raise_for_status()
        return response.json()
