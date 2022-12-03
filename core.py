import numpy as np
from datetime import datetime
import pandas_datareader.data as pdr
import pandas as pd

def get_returns(historical_prices,log_retun=False):
    """
        retuns and logreturns
    """
    if log_retun:
        return np.log(historical_prices/ historical_prices.shift(1)).dropna()

    else:
        return historical_prices.pct_change().dropna()

def HVar(tickers, start_date, end_date, time_interval,log_retun=False):

    historical_prices = pd.DataFrame()
    for t in tickers:
        historical_prices[t] = pdr.YahooDailyReader(t, interval=time_interval , start=start_date,end=end_date).read()['Adj Close']
    
    historical_returns = get_returns(historical_prices)

    alpha = 0.01
    num_shares = 5000
    on_date = historical_prices.index.max()

    for t in tickers:

        share_price = historical_prices[t].loc[on_date]
        # No assumption involved use the theoretical distribution
        daily_return_rates = historical_returns[t].dropna().sort_values().reset_index(drop=True)
        

        xth = int(np.floor(0.01*len(daily_return_rates))) - 1
        xth_smallest_rate = daily_return_rates[xth]

        mean_return_rate = daily_return_rates.mean()

        rel_VaR = num_shares * share_price * (mean_return_rate - xth_smallest_rate)
        abs_VaR = -num_shares * share_price * xth_smallest_rate

        print("The estimated relative VaR and absolute VaR of an investment of", num_shares, "shares of", t, "on", on_date, "with price $", round(share_price,2), "per share is $", round(rel_VaR,2), "and $", round(abs_VaR,2), "respectively.")

