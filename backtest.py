# -*- coding: utf-8 -*-
"""
Created on Mon Mar  4 10:29:08 2019

@author: helleju
"""

from src import *

data_handler = BloombergAPI(SERVER_HOST='localhost',SERVER_PORT=8194)
start_date   = datetime(2000,1,1)
end_date     = datetime(2019,1,1)
price_data   = []
for symbol in symbols:
    print(symbol)
    try:
        bloomberg_symbol = symbol+' US Equity'
        data = data_handler.send_request([bloomberg_symbol],["PX_LAST"],start_date,end_date)
        if(len(data[bloomberg_symbol])!=0):
            f = pandas.DataFrame.from_dict(data[bloomberg_symbol],orient='index')
            f.columns = [bloomberg_symbol]
            price_data.append(f.copy())
    except:
        print(f"Could not download data for {symbol}")

price_data = pandas.concat(price_data,axis=1)
price_data.index = pandas.DatetimeIndex(price_data.index)
