import time
import json
import requests
from eth_account import Account
from eth_account.messages import encode_defunct, encode_typed_data
try:
    from .config import Config
except ImportError:
    from config import Config

class LimitlessAuth:
    def __init__(self):
        Config.validate()
        self.account = Account.from_key(Config.PRIVATE_KEY)
        self.session_cookie = None
        self.user_data = None
        self.api_url = Config.API_URL

    def get_address(self):
        return self.account.address

    def get_signing_message(self):
        """Fetch the signing message from the API."""
        response = requests.get(f"{self.api_url}/auth/signing-message")
        response.raise_for_status()
        return response.text

    def login(self):
        """Authenticate with the API and store the session cookie."""
        signing_message = self.get_signing_message()
        
        # Sign the message (standard Ethereum message signing for login)
        message = encode_defunct(text=signing_message)
        signed_message = self.account.sign_message(message)
        signature = signed_message.signature.hex()
        
        headers = {
            "x-account": self.account.address,
            "x-signing-message": "0x" + signing_message.encode("utf-8").hex(),
            "x-signature": signature if signature.startswith("0x") else "0x" + signature,
            "Content-Type": "application/json"
        }
        
        response = requests.post(
            f"{self.api_url}/auth/login",
            headers=headers,
            json={"client": "eoa"}
        )
        response.raise_for_status()
        
        self.session_cookie = response.cookies.get("limitless_session")
        self.user_data = response.json()
        print(f"Authenticated as: {self.user_data.get('account')}")
        return self.session_cookie

    def sign_order(self, order_payload, market_type="CLOB"):
        """Sign an order using EIP-712."""
        contract_address = Config.CLOB_CFT_ADDR if market_type == "CLOB" else Config.NEGRISK_CFT_ADDR
        
        domain_data = {
            "name": "Limitless CTF Exchange",
            "version": "1",
            "chainId": Config.CHAIN_ID,
            "verifyingContract": contract_address,
        }
        
        order_types = {
            "Order": [
                {"name": "salt", "type": "uint256"},
                {"name": "maker", "type": "address"},
                {"name": "signer", "type": "address"},
                {"name": "taker", "type": "address"},
                {"name": "tokenId", "type": "uint256"},
                {"name": "makerAmount", "type": "uint256"},
                {"name": "takerAmount", "type": "uint256"},
                {"name": "expiration", "type": "uint256"},
                {"name": "nonce", "type": "uint256"},
                {"name": "feeRateBps", "type": "uint256"},
                {"name": "side", "type": "uint8"},
                {"name": "signatureType", "type": "uint8"},
            ]
        }
        
        # Ensure types are correct for signing
        message_data = {
            "salt": int(order_payload["salt"]),
            "maker": order_payload["maker"],
            "signer": order_payload["signer"],
            "taker": order_payload["taker"],
            "tokenId": int(order_payload["tokenId"]),
            "makerAmount": int(order_payload["makerAmount"]),
            "takerAmount": int(order_payload["takerAmount"]),
            "expiration": int(order_payload["expiration"]),
            "nonce": int(order_payload["nonce"]),
            "feeRateBps": int(order_payload["feeRateBps"]),
            "side": int(order_payload["side"]),
            "signatureType": int(order_payload["signatureType"]),
        }
        
        encoded_message = encode_typed_data(domain_data, order_types, message_data)
        signed_message = self.account.sign_message(encoded_message)
        
        return signed_message.signature.hex()
