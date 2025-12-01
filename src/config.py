import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    API_URL = os.getenv("API_URL", "https://api.limitless.exchange")
    CHAIN_ID = int(os.getenv("CHAIN_ID", "8453"))
    
    # Contract Addresses
    CLOB_CFT_ADDR = os.getenv("CLOB_CFT_ADDR", "0xa4409D988CA2218d956BeEFD3874100F444f0DC3")
    NEGRISK_CFT_ADDR = os.getenv("NEGRISK_CFT_ADDR", "0x5a38afc17F7E97ad8d6C547ddb837E40B4aEDfC6")
    
    # Wallet
    PRIVATE_KEY = os.getenv("PRIVATE_KEY")

    @classmethod
    def validate(cls):
        if not cls.PRIVATE_KEY:
            raise ValueError("PRIVATE_KEY environment variable is not set. Please check your .env file.")
