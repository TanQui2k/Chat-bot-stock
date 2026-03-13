"""Quick test to register vnstock API key."""
import sys
sys.stdout.reconfigure(encoding='utf-8')
import os
os.environ['VNSTOCK_API_KEY'] = 'vnstock_48ee0184c86e49da9a5fea282ad3e2ea'

from vnstock import Vnstock
stock = Vnstock().stock(symbol='FPT', source='VCI')
history = stock.quote.history(start='2018-01-01', end='2018-01-31')
print(f"Fetched {len(history)} rows for FPT Jan 2018")
print(history.head(3))
