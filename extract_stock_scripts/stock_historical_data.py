import pandas as pd
import datetime
import pandas.io.data as web
import matplotlib.pyplot as plt


"""
Get historical data of stocks by specifying time range.
Uses Yahoo Finance API
"""

start = datetime.datetime(2016, 10, 18)
end = datetime.datetime(2016, 10, 18)
df = web.DataReader("GOOGL", "yahoo", start, end)

print(df)