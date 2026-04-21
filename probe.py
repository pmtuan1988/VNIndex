import vnstock
import pandas as pd
import importlib.metadata
print(f"vnstock version: {importlib.metadata.version('vnstock')}")

s = vnstock.Vnstock().stock(symbol='SHB', source='KBS')
print(f"Stock object methods: {[m for m in dir(s) if not m.startswith('_')]}")
print(f"Quote methods: {[m for m in dir(s.quote) if not m.startswith('_')]}")

df = s.quote.history(start='2023-01-01', end='2023-12-31')
print(df.tail(2))
