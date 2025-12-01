import time
import sys
import os

# Add src to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import Config
from api_client import LimitlessClient
from strategy import SimpleStrategy

def main():
    print("Starting Limitless Trading Bot...")
    
    try:
        # 1. Initialize Client
        client = LimitlessClient()
        print("API Client initialized.")
        
        # 2. Initialize Strategy
        # We can make this configurable via args later
        strategy = SimpleStrategy(client)
        print(f"Strategy {strategy.__class__.__name__} initialized.")
        
        # 3. Main Loop
        print("Entering main loop. Press Ctrl+C to stop.")
        while True:
            strategy.run()
            
            # Sleep to avoid rate limits and spamming
            time.sleep(10)
            
    except KeyboardInterrupt:
        print("\nBot stopped by user.")
    except Exception as e:
        print(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
