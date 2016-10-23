from googlefinance import getQuotes
import json

"""
Get today's stock market data
"""

print json.dumps(getQuotes('GOOGL'), indent=2)

