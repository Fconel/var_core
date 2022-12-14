import core
from datetime import datetime

def main():
    tickers = {'GOOG':500,'MSFT':600}
    start_date = datetime.strptime('2018-01-01', '%Y-%m-%d')
    end_date = datetime.strptime('2021-03-10', '%Y-%m-%d')
    time_interval='d'

    value_at_risk=core.HVar(tickers, start_date, end_date, time_interval, alpha = 0.05,decay=True,decay_rate=0.95)

    print(value_at_risk)

if __name__ == "__main__":

    main()