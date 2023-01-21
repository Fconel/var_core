import core
from datetime import datetime

def main(model):
    tickers = {'GOOG':500,'MSFT':600}
    start_date = datetime.strptime('2018-01-01', '%Y-%m-%d')
    end_date = datetime.strptime('2021-03-10', '%Y-%m-%d')
    time_interval='1d'

    if model == 'HVaR':
        return core.HVar(tickers, start_date, end_date, time_interval, alpha = 0.05,decay_rate=0.99)
    if model == 'PVaR':
        return core.PVar(tickers, start_date, end_date, time_interval, alpha = 0.05,decay_rate=None)
    else:
        raise Exception(NotImplemented)


if __name__ == "__main__":

    print(main('PVaR'))