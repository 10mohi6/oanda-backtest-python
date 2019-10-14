import requests
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os

class Backtest(object):

    def __init__(self, *, token):
        self._headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer {}".format(token)
        }
        self._base_url = "https://api-fxpractice.oanda.com"
        self._limit = 0
        self._expiration = 10
        self._point = 0.0001 # 1pips
        self._lots = 10000 # currency unit
        self._take_profit = 0
        self._stop_loss = 0
        self._spread = 0
        self._initial_deposit = 0

    def _request(self, path, params=None):
        uri = "{}{}".format(self._base_url, path)
        return requests.get(uri, headers=self._headers, params=params)

    def get(self, instrument, params=None):
        path = "/v3/instruments/{}/candles".format(instrument)
        res = self._request(path, params=params)
        data = []
        for r in res.json()['candles']:
            data.append([pd.to_datetime(r['time']), float(r['mid']['o']), float(r['mid']['h']), float(r['mid']['l']), float(r['mid']['c']), float(r['volume'])])
        self.df = pd.DataFrame(data, columns=['T', 'O', 'H', 'L', 'C', 'V']).set_index('T')
        return self.df

    def exists(self, filepath):
        return os.path.exists(filepath)

    def to_csv(self, filepath):
        return self.df.to_csv(filepath)

    def read_csv(self, filepath):
        self.df = pd.read_csv(filepath, index_col=0, parse_dates=True, infer_datetime_format=True)
        return self.df

    def sma(self, *, period, price="C"):
        return self.df[price].rolling(period).mean()

    def ema(self, *, period, price="C"):
        return self.df[price].ewm(span=period).mean()

    def bband(self, *, period=20, band=2, price="C"):
        std = self.df[price].rolling(period).std()
        mean = self.df[price].rolling(period).mean()
        return mean - (std * band), mean + (std * band)
    
    def macd(self, *, fast_period=12, slow_period=26, signal_period=9, price="C"):
        macd = self.df[price].ewm(span=fast_period).mean() - self.df[price].ewm(span=slow_period).mean()
        signal = macd.ewm(span=signal_period).mean()
        return macd, signal
    
    def stoch(self, *, k_period=5, d_period=3):
        k = (self.df.C - self.df.L.rolling(k_period).min()) / (self.df.H.rolling(k_period).max() - self.df.L.rolling(k_period).min()) * 100
        d = k.rolling(d_period).mean()
        return k, d

    def mom(self, *, period=10, price="C"):
        return self.df[price].diff(period)
    
    def rsi(self, *, period=14, price="C"):
        return 100 - 100 / (1 - self.df[price].diff().clip(lower=0).rolling(period).mean() / self.df[price].diff().clip(upper=0).rolling(period).mean())

    @property
    def buy_entry(self):
        return self._buy_entry

    @buy_entry.setter
    def buy_entry(self, buy_entry):
        self._buy_entry = buy_entry

    @property
    def sell_entry(self):
        return self._sell_entry

    @sell_entry.setter
    def sell_entry(self, sell_entry):
        self._sell_entry = sell_entry

    @property
    def buy_exit(self):
        return self._buy_exit

    @buy_exit.setter
    def buy_exit(self, buy_exit):
        self._buy_exit = buy_exit

    @property
    def sell_exit(self):
        return self._sell_exit

    @sell_exit.setter
    def sell_exit(self, sell_exit):
        self._sell_exit = sell_exit

    @property
    def limit(self):
        return self._limit

    @limit.setter
    def limit(self, limit):
        self._limit = limit

    @property
    def expiration(self):
        return self._expiration

    @expiration.setter
    def expiration(self, expiration):
        self._expiration = expiration

    @property
    def point(self):
        return self._point

    @point.setter
    def point(self, point):
        self._point = point

    @property
    def lots(self):
        return self._lots

    @lots.setter
    def lots(self, lots):
        self._lots = lots

    @property
    def take_profit(self):
        return self._take_profit

    @take_profit.setter
    def take_profit(self, take_profit):
        self._take_profit = take_profit

    @property
    def stop_loss(self):
        return self._stop_loss

    @stop_loss.setter
    def stop_loss(self, stop_loss):
        self._stop_loss = stop_loss

    @property
    def spread(self):
        return self._spread

    @spread.setter
    def spread(self, spread):
        self._spread = spread

    @property
    def initial_deposit(self):
        return self._initial_deposit

    @initial_deposit.setter
    def initial_deposit(self, initial_deposit):
        self._initial_deposit = initial_deposit

    @property
    def C(self):
        return self.df.C

    @property
    def O(self):
        return self.df.O

    @property
    def H(self):
        return self.df.H

    @property
    def L(self):
        return self.df.L

    @property
    def V(self):
        return self.df.V

    def run(self):
        o = self.df.O.values
        l = self.df.L.values
        h = self.df.H.values
        N = len(self.df)

        long_trade = np.zeros(N)
        short_trade = np.zeros(N)

        # buy entry
        buy_entry_s = np.hstack((False, self._buy_entry[:-1])) # shift
        if self._limit == 0:
            # market buy
            long_trade[buy_entry_s] = o[buy_entry_s] + self._spread
        else:
            # limit buy
            for i in range(N - self._expiration):
                if buy_entry_s[i]:
                    buy_limit = o[i] - self._limit * self._point
                    for j in range(self._expiration):
                        if l[i+j] <= buy_limit: # contract conditions
                            long_trade[i+j] = buy_limit + self._spread
                            break

        # buy exit
        buy_exit_s = np.hstack((False, self._buy_exit[:-2], True)) # shift
        long_trade[buy_exit_s] = -o[buy_exit_s]

        # sell entry
        sell_entry_s = np.hstack((False, self._sell_entry[:-1])) # shift
        if self._limit == 0:
            # market sell
            short_trade[sell_entry_s] = o[sell_entry_s]
        else:
            # limit sell
            for i in range(N - self._expiration):
                if sell_entry_s[i]:
                    sell_limit = o[i] + self._limit * self._point
                    for j in range(self._expiration):
                        if h[i+j] >= sell_limit: # contract conditions
                            short_trade[i+j] = sell_limit
                            break

        # sell exit
        sell_exit_s = np.hstack((False, self._sell_exit[:-2], True)) # shift
        short_trade[sell_exit_s] = -(o[sell_exit_s] + self._spread)

        long_pl = pd.Series(np.zeros(N)) # profit/loss of buy position
        short_pl = pd.Series(np.zeros(N)) # profit/loss of sell position
        buy_price = sell_price = 0
        long_rr = [] # long return rate
        short_rr = [] # short return rate
        stop_loss = take_profit = 0

        for i in range(1,N):
            # buy entry
            if long_trade[i] > 0: 
                if buy_price == 0:
                    buy_price = long_trade[i]
                    short_trade[i] = -buy_price # sell exit
                else: long_trade[i] = 0
            
            # sell entry
            if short_trade[i] > 0: 
                if sell_price == 0:
                    sell_price = short_trade[i]
                    long_trade[i] = -sell_price # buy exit
                else: short_trade[i] = 0

            # buy exit
            if long_trade[i] < 0: 
                if buy_price != 0:
                    long_pl[i] = -(buy_price+long_trade[i])*self._lots # profit/loss fixed
                    long_rr.append(round(long_pl[i] / buy_price * 100, 2)) # long return rate
                    buy_price = 0
                else: long_trade[i] = 0

            # sell exit
            if short_trade[i] < 0: 
                if sell_price != 0:
                    short_pl[i] = (sell_price+short_trade[i])*self._lots # profit/loss fixed
                    short_rr.append(round(short_pl[i] / sell_price * 100, 2)) # short return rate
                    sell_price = 0
                else: short_trade[i] = 0

            # close buy position with stop loss
            if buy_price != 0 and self._stop_loss > 0: 
                stop_price = buy_price-self._stop_loss*self._point
                if l[i] <= stop_price:
                    long_trade[i] = -stop_price
                    long_pl[i] = -(buy_price+long_trade[i])*self._lots # profit/loss fixed
                    long_rr.append(round(long_pl[i] / buy_price * 100, 2)) # long return rate
                    buy_price = 0
                    stop_loss += 1

            # close buy positon with take profit
            if buy_price != 0 and self._take_profit > 0:
                limit_price = buy_price+self._take_profit*self._point
                if h[i] >= limit_price:
                    long_trade[i] = -limit_price
                    long_pl[i] = -(buy_price+long_trade[i])*self._lots # profit/loss fixed
                    long_rr.append(round(long_pl[i] / buy_price * 100, 2)) # long return rate
                    buy_price = 0
                    take_profit += 1

            # close sell position with stop loss
            if sell_price != 0 and self._stop_loss > 0:
                stop_price = sell_price+self._stop_loss*self._point
                if h[i]+self._spread >= stop_price:
                    short_trade[i] = -stop_price
                    short_pl[i] = (sell_price+short_trade[i])*self._lots # profit/loss fixed
                    short_rr.append(round(short_pl[i] / sell_price * 100, 2)) # short return rate
                    sell_price = 0
                    stop_loss += 1

            # close sell position with take profit
            if sell_price != 0 and self._take_profit > 0:
                limit_price = sell_price-self._take_profit*self._point
                if l[i]+self._spread <= limit_price:
                    short_trade[i] = -limit_price
                    short_pl[i] = (sell_price+short_trade[i])*self._lots # profit/loss fixed
                    short_rr.append(round(short_pl[i] / sell_price * 100, 2)) # short return rate
                    sell_price = 0
                    take_profit += 1

        win_trades = np.count_nonzero(long_pl.clip(lower=0)) + np.count_nonzero(short_pl.clip(lower=0))
        lose_trades = np.count_nonzero(long_pl.clip(upper=0)) + np.count_nonzero(short_pl.clip(upper=0))
        trades = (np.count_nonzero(long_trade)//2) + (np.count_nonzero(short_trade)//2)
        gross_profit = long_pl.clip(lower=0).sum() + short_pl.clip(lower=0).sum()
        gross_loss = long_pl.clip(upper=0).sum() + short_pl.clip(upper=0).sum()
        profit_pl = gross_profit + gross_loss
        self.equity = (long_pl + short_pl).cumsum()
        mdd = (self.equity.cummax() - self.equity).max()
        self.return_rate = pd.Series(short_rr+long_rr)
        
        s = pd.Series()
        s.loc['total profit'] = round(profit_pl, 2)
        s.loc['total trades'] = trades
        s.loc['win rate'] = round(win_trades / trades * 100, 2)
        s.loc['profit factor'] = round(-gross_profit / gross_loss, 2)
        s.loc['maximum drawdown'] = round(mdd, 2)
        s.loc['recovery factor'] = round(profit_pl / mdd, 2)
        s.loc['riskreward ratio'] = round(-(gross_profit / win_trades) / (gross_loss / lose_trades), 2)
        s.loc['sharpe ratio'] = round(self.return_rate.mean() / self.return_rate.std(), 2)
        s.loc['average return'] = round(self.return_rate.mean(), 2)
        s.loc['stop loss'] = stop_loss
        s.loc['take profit'] = take_profit
        return s

    def plot(self, filepath=None):
        plt.subplot(2, 1, 1)
        plt.plot(self.equity+self._initial_deposit, label="equity")
        plt.legend()
        plt.subplot(2, 1, 2)
        plt.hist(self.return_rate, 50, rwidth=0.9)
        plt.axvline(sum(self.return_rate)/len(self.return_rate), color="orange", label="average return")
        plt.legend()
        if filepath is None:
            plt.show()
        else:
            plt.savefig(filepath)
