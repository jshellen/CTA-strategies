# -*- coding: utf-8 -*-
"""
Created on Wed Mar 13 13:21:52 2019

@author: helleju
"""

from src.data_request import BloombergAPI
from datetime import datetime
import pandas as pd
import numpy  as np

import warnings
warnings.filterwarnings('ignore')

securities = {'ED5 Comdty'    : {'Symbol':'ED5 Comdty'},
              'ED6 Comdty'    : {'Symbol':'ED6 Comdty'},
              'ED7 Comdty'    : {'Symbol':'ED7 Comdty'},
              'ED8 Comdty'    : {'Symbol':'ED8 Comdty'},
              'ED9 Comdty'    : {'Symbol':'ED9 Comdty'},
              'ED10 Comdty'    : {'Symbol':'ED10 Comdty'},
              'ED11 Comdty'    : {'Symbol':'ED11 Comdty'},
                       }


#securities = {
##        'ED2 Comdty'    : {'Symbol':'ED2 Comdty'},
##              
##              'ED4 Comdty'    : {'Symbol':'ED4 Comdty'},
##              
##              'ED6 Comdty'    : {'Symbol':'ED6 Comdty'},
##             
##              'ED8 Comdty'    : {'Symbol':'ED8 Comdty'},
#           
#              'ED10 Comdty'    : {'Symbol':'ED10 Comdty'},
#              
#              'ED12 Comdty'    : {'Symbol':'ED12 Comdty'},
#              
#              'ED15 Comdty'    : {'Symbol':'ED15 Comdty'},
#              
#              'ED18 Comdty'    : {'Symbol':'ED18 Comdty'},
#                       }


securities = {
              'CL1 Comdty'  : {'Symbol':'CL1 Comdty' },
              'HO1 Comdty'  : {'Symbol':'HO1 Comdty' },
              #'XB1 Comdty'  : {'Symbol':'XB1 Comdty' },
              
             }



symbols = [ securities[s]['Symbol'] for s in list(securities.keys())]


# Download data for traded instruments
data_handler = BloombergAPI(SERVER_HOST='localhost',SERVER_PORT=8194)
start_date   = datetime(2010,10,7)
end_date     = datetime.today()
price_data   = []
for symbol in symbols:
    print('Downloading data for symbol :',symbol)
    try:
        data = data_handler.send_request([symbol],["PX_LAST"],start_date,end_date)
        if(len(data[symbol])!=0):
            f = pd.DataFrame.from_dict(data[symbol],orient='index')
            f.columns = [symbol]
            price_data.append(f.copy())
    except:
        print(f"Could not download data for {symbol}")

price_data       = pd.concat(price_data,axis=1)
price_data.index = pd.DatetimeIndex(price_data.index)
price_data = price_data.fillna(method='ffill')

#%%
# Cannot use shift operation here because of sparse dates

fit_start = datetime(2010,10,7)
fit_end   = datetime(2018,10,1)

S     = price_data.loc[fit_start:fit_end].dropna().as_matrix()
S_lag = np.roll(S,1,axis=0)

S     = S[1:,:]
S_lag = S_lag[1:,:]

print(S)
print(S_lag)


#%% Estimate A
    
A_1 = np.linalg.pinv(np.transpose(S_lag).dot(S_lag))
A_2 = np.transpose(S_lag).dot(S)
A   = A_1.dot(A_2)

#%% Estimate Bewley et al

from scipy.linalg import sqrtm

Gamma = price_data.loc[fit_start:fit_end].dropna().cov().as_matrix()

M_1 = np.linalg.pinv(sqrtm(Gamma)).dot(A.T)
M_2 = A.dot( np.linalg.pinv(sqrtm(Gamma)))

M   = M_1.dot(Gamma).dot(M_2)


#%%

evals,evecs = np.linalg.eig(M)


idx   = evals.argsort()[::-1]   
evals = evals[idx]
evecs = evecs[:,idx]

#%%
import matplotlib.pyplot as plt

# Get the last eigenvector
z = evecs[:,M.shape[1]-1]

# Normalize weights
z = np.divide(z,z[0])

x = np.linalg.pinv(sqrtm(Gamma)).dot(z)


weights = np.multiply(x,np.ones_like(price_data))

y = (weights*price_data.fillna(method='ffill')).sum(axis=1)

y.tail(2000).plot()

z_score = ((y-y.ewm(50).mean())/y.ewm(250).std()).clip(-1,1)

z_score.plot()


fig=plt.figure(figsize=(10,10))

perf = ((-z_score.shift(1))*(weights*price_data.pct_change(1).fillna(0)).mean(axis=1)).cumsum()

plt.plot(perf)







