import numpy as np
from datetime import datetime
import pandas_datareader.data as pdr
import pandas as pd
import scipy.stats as stats

def get_prices(tickers, start_date, end_date, time_interval,source='yahoo'):
    '''
    Function to get prices from diferent sources
    '''
    if source == 'yahoo':

        import yfinance as yf

        yf.pdr_override() #use yfinance package to override pandas_datareader, this package are  more up to date concerning yahoo encripting the data

        return pdr.get_data_yahoo(tickers, interval=time_interval , start=start_date,end=end_date,progress=False)['Adj Close']
    
    else:

        raise Exception("Source not suported")

def get_returns(*args, **kwargs):

    '''TBI'''
    return None

def get_returns(prices,log_retun=False):
    '''
    Simpe function to get Returns or logReturns
    '''
    if log_retun:

        return np.log(prices/ prices.shift(1)).dropna()

    else:

        return prices.pct_change().dropna()

def decay_returns(return_portfolio,decay_rate):

    Decay_vector = [(decay_rate**(i-1) * (1-decay_rate))/(1-decay_rate**len(return_portfolio)) for i in range(1, len(return_portfolio)+1)]

    return_portfolio_weighted = return_portfolio[::-1]
    decay_returns = pd.DataFrame({'returns': return_portfolio_weighted,'decay': Decay_vector}).sort_values(by='returns')
    decay_returns['cumulative'] = decay_returns.decay.cumsum()
    decay_returns = decay_returns.reset_index().drop(columns=['index'])
    index=(decay_returns[decay_returns.cumulative <= (1-decay_rate)].returns.idxmax())
    xp = decay_returns.loc[index:index+1, 'cumulative'].values
    fp = decay_returns.loc[index:index+1, 'returns'].values
    
    return  np.interp((1-decay_rate), xp, fp) 

def Value_at_risk_over_n_days(Value_at_risk,number_of_periods,portfolio_value):
    '''
    Return a dataframe with a list of VaR for n days:
    It is useful to make graphs of the evolution of VAR
    '''
    df = pd.DataFrame(columns = ['N of periods','Value at Risk rate' ,'Value at Risk'])

    for x in range(number_of_periods):

        Value_at_Risk_rate = Value_at_risk * np.sqrt(x+1)

        df_new_row = pd.DataFrame.from_records({ 'N' : int(x+1), 'Value at Risk rate' : np.round(Value_at_Risk_rate,2),'Value at Risk':np.round(Value_at_Risk_rate*portfolio_value,0)},[x])
        df = pd.concat([df, df_new_row], ignore_index=True)
        
    return df

def HVar(tickers, start_date, end_date, time_interval,log_retun=False,alpha=0.05,decay_rate=None):
    '''
    tickers variable must by a dictionary whit ticket and quantity
    '''
    tickers_list=list(tickers.keys())

    assets_prices = get_prices(tickers_list, start_date, end_date, time_interval)
        
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

    ####Model approaches####

    #Equally Weighted Var (**Default**)
    return_portfolio = assets_returns.mul(portfolio_weights.values).sum(axis = 1).dropna().reset_index(drop=True)
    return_portfolio_sorted = return_portfolio.sort_values()
    mean_return_rate = return_portfolio_sorted.mean()

    Value_at_Risk = return_portfolio_sorted.quantile(alpha, interpolation="lower")
    expected_shortfall = return_portfolio_sorted[return_portfolio_sorted < Value_at_Risk].dropna().mean()
    
    #Bootstrap VaR
    '''TBI'''
    #Volatility-Weighted VaR
    '''TBI'''
    #Filtered Historical Simulation
    '''TBI'''

    ####model expansions####

    #Age-Weighted VaR (decay factor)
    if decay_rate is not None:

        Value_at_Risk = decay_returns(return_portfolio,decay_rate)


    return {"Portfolio Value": portfolio_value, "Value at Risk rate":Value_at_Risk,"Value at Risk":-Value_at_Risk*portfolio_value,'Expected shortfall':expected_shortfall,'returns':return_portfolio}

def PVar(tickers, start_date, end_date, time_interval,log_retun=False,alpha=0.05,decay_rate=None):
    '''
    tickers variable must by a dictionary whit ticket and quantity
    '''
    tickers_list=list(tickers.keys())

    assets_prices = get_prices(tickers_list, start_date, end_date, time_interval)
        
    assets_value = assets_prices.iloc[:, 0:]  * list(tickers.values())
    assets_returns = get_returns(assets_prices)

    portfolio_weights = assets_value.div(assets_value.sum(axis = 1), axis=0).tail(-1)

    on_date = assets_prices.index.max()
    portfolio_value = assets_value.loc[on_date].sum()
   
    if not portfolio_weights.index.equals(assets_returns.index):
        '''
        add safeguards here
        '''
        raise Exception("no hay retornos para todos los pesos, seguramente no hay precios de algun ticker para alguna fecha")

    #Metric by total portfolio

    return_portfolio = assets_returns.mul(portfolio_weights.values).sum(axis = 1).dropna().reset_index(drop=True)
    portfolio_weights_ondate = portfolio_weights.loc[on_date]
  
    cov_matrix = assets_returns.cov()



    port_stdev = np.sqrt(portfolio_weights_ondate.T.dot(cov_matrix).dot(portfolio_weights_ondate))

    port_mean  = return_portfolio.mean() 
    expected_shortfall = alpha**-1 * stats.norm.pdf(stats.norm.ppf(alpha))*port_stdev - port_mean

    Value_at_Risk = stats.norm.ppf(alpha, port_mean, port_stdev)

    if decay_rate is not None:
        '''
        TBI
        '''
        raise Exception(NotImplemented)

    return {"Portfolio Value": portfolio_value, "Value at Risk rate":Value_at_Risk,"Value at Risk":-Value_at_Risk*portfolio_value,'Expected shortfall':expected_shortfall,'returns':return_portfolio}