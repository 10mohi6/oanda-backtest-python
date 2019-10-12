import os, pytest
from oanda_backtest import Backtest

class TestBacktest(object):

    def setup_method(self, method):
        token = os.environ['oanda_backtest_token']
        self.bt = Backtest(token=token)

    def test_run_basic(self):

        self.bt.get("EUR_USD")
        fast_ma = self.bt.sma(period=5)
        slow_ma = self.bt.sma(period=25)
        self.bt.sell_exit = self.bt.buy_entry = ((fast_ma > slow_ma) & (fast_ma.shift() <= slow_ma.shift())).values
        self.bt.buy_exit = self.bt.sell_entry = ((fast_ma < slow_ma) & (fast_ma.shift() >= slow_ma.shift())).values
        actual = self.bt.run()
        expected = 11
        assert expected == len(actual)

    def test_run_advanced(self):

        filepath='usd-jpy-h1.csv'
        if os.path.exists(filepath):
            self.bt.read_csv(filepath)
        else:
            self.bt.get("USD_JPY", {"granularity": "H1", "count": 5000})
            self.bt.to_csv(filepath)

        fast_ma = self.bt.sma(period=10)
        slow_ma = self.bt.sma(period=30)
        exit_ma = self.bt.sma(period=5)
        self.bt.buy_entry = ((fast_ma > slow_ma) & (fast_ma.shift() <= slow_ma.shift())).values
        self.bt.sell_entry = ((fast_ma < slow_ma) & (fast_ma.shift() >= slow_ma.shift())).values
        self.bt.buy_exit = ((self.bt.C < exit_ma) & (self.bt.C.shift() >= exit_ma.shift())).values
        self.bt.sell_exit = ((self.bt.C > exit_ma) & (self.bt.C.shift() <= exit_ma.shift())).values

        self.bt.initial_deposit = 100000
        self.bt.point = 0.01
        self.bt.spread = 0.08
        self.bt.limit = 20
        self.bt.loss_cut = 50
        self.bt.lots = 10000
        self.bt.profit_taking = 100

        actual = self.bt.run()
        self.bt.plot("backtest.png")
        expected = 11
        assert expected == len(actual)
