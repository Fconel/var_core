import numpy as np
from datetime import datetime
import pandas_datareader.data as pdr
import pandas as pd
import scipy.stats as stats

def get_returns(prices,log_retun=False):
    
    if log_retun:
        return np.log(prices/ prices.shift(1)).dropna()

    else:
        return prices.pct_change().dropna()

def HVar(tickers, start_date, end_date, time_interval,log_retun=False,alpha=0.05,decay=False,decay_rate=0.95):

    assets_prices = pdr.YahooDailyReader(list(tickers.keys()), interval=time_interval , start=start_date,end=end_date).read()['Adj Close']

    assets_value = assets_prices.iloc[:, 0:]  * list(tickers.values())
    assets_returns = get_returns(assets_prices)
    portfolio_weights = assets_value.div(assets_value.sum(axis = 1), axis=0).tail(-1)
    on_date = assets_prices.index.max()
    portfolio_value = assets_value.loc[on_date].sum()
   
    if not portfolio_weights.index.equals(assets_returns.index):
        '''
        add safeguards here
        '''
        raise Exception("no hay retornos para todos los pesos")

    #by portfolio
    
    return_portfolio = assets_returns.mul(portfolio_weights.values).sum(axis = 1).dropna().reset_index(drop=True)
    return_portfolio_sorted = return_portfolio.sort_values()

    xth_smallest_rate = return_portfolio_sorted.quantile(alpha, interpolation="lower")
    expected_shortfall = return_portfolio_sorted[return_portfolio_sorted < xth_smallest_rate].dropna().mean()
    mean_return_rate = return_portfolio_sorted.mean()
    abs_VaR = portfolio_value * xth_smallest_rate
    
    #by asset
    '''
    Soon add metrics by asset 
    '''

    if decay:

        Decay_vector = [(decay_rate**(i-1) * (1-decay_rate))/(1-decay_rate**len(return_portfolio)) for i in range(1, len(return_portfolio)+1)] 
        return_portfolio_weighted = return_portfolio[::-1]
        decay_returns = pd.DataFrame({'returns': return_portfolio_weighted,'decay': Decay_vector}).sort_values(by='returns')
        decay_returns['cumulative'] = decay_returns.decay.cumsum()

        decay_returns = decay_returns.reset_index().drop(columns=['index'])
        decay_returns[decay_returns.cumulative <= 0.05].returns.idxmax()
        
        index=(decay_returns[decay_returns.cumulative <= 0.05].returns.idxmax())
        
        xp = decay_returns.loc[index:index+1, 'cumulative'].values
        fp = decay_returns.loc[index:index+1, 'returns'].values
        VaR_weighted = np.interp(0.05, xp, fp) 
        
        return {"Portfolio Value": portfolio_value, "absolute Age-weighted VaR ":portfolio_value*VaR_weighted, "Age-weighted VaR is " :VaR_weighted,'Expected shortfall':expected_shortfall}

    return {"Portfolio Value": portfolio_value, "absolute VaR":abs_VaR, "perc" :xth_smallest_rate,'Expected shortfall':expected_shortfall}

def PVar(tickers, start_date, end_date, time_interval,log_retun=False,alpha=0.05):
    
    '''
    soon
    '''
    return None