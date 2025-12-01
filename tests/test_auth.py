import unittest
import os
import sys
from unittest.mock import patch, MagicMock

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from auth import LimitlessAuth
from config import Config

class TestAuth(unittest.TestCase):
    def setUp(self):
        # Mock environment variables
        self.env_patcher = patch.dict(os.environ, {
            "PRIVATE_KEY": "0x0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
            "API_URL": "https://api.limitless.exchange",
            "CHAIN_ID": "8453"
        })
        self.env_patcher.start()
        
        # Reload config to pick up mocked env
        import importlib
        importlib.reload(sys.modules['config'])
        
    def tearDown(self):
        self.env_patcher.stop()

    def test_sign_order(self):
        auth = LimitlessAuth()
        
        order_payload = {
            "salt": 123456789,
            "maker": auth.get_address(),
            "signer": auth.get_address(),
            "taker": "0x0000000000000000000000000000000000000000",
            "tokenId": "123",
            "makerAmount": 1000000,
            "takerAmount": 1000000,
            "expiration": 0,
            "nonce": 0,
            "feeRateBps": 0,
            "side": 0,
            "signatureType": 0,
        }
        
        signature = auth.sign_order(order_payload)
        self.assertTrue(signature.startswith("0x") or len(signature) == 130) # 130 chars for hex signature (65 bytes)
        print(f"Generated signature: {signature}")

if __name__ == '__main__':
    unittest.main()
