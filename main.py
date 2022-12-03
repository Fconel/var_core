import core
from datetime import datetime

tickers = ['GOOG','MSFT']
start_date = datetime.strptime('2018-01-01', '%Y-%m-%d')
end_date = datetime.strptime('2021-03-10', '%Y-%m-%d')
time_interval='d'

if __name__ == "__main__":

    core.HVar(tickers, start_date, end_date, time_interval)

