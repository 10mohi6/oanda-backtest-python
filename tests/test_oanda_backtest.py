import os
from oanda_backtest import Backtest


class TestBacktest(object):
    def setup_method(self, method):
        access_token = os.environ["oanda_backtest_token"]
        self.bt = Backtest(access_token=access_token, environment="practice")

    def test_run_basic(self):

        self.bt.candles("EUR_USD")
        fast_ma = self.bt.sma(period=5)
        slow_ma = self.bt.sma(period=25)
        self.bt.sell_exit = self.bt.buy_entry = (fast_ma > slow_ma) & (
            fast_ma.shift() <= slow_ma.shift()
        )
        self.bt.buy_exit = self.bt.sell_entry = (fast_ma < slow_ma) & (
            fast_ma.shift() >= slow_ma.shift()
        )

        actual = self.bt.run()
        expected = 11
        assert expected == len(actual)

    def test_run_advanced(self):

        filepath = "usd-jpy-h1.csv"
        if self.bt.exists(filepath):
            self.bt.read_csv(filepath)
        else:
            self.bt.candles("USD_JPY", {"granularity": "H1", "count": "5000"})
            self.bt.to_csv(filepath)

        fast_ma = self.bt.sma(period=10)
        slow_ma = self.bt.sma(period=30)
        exit_ma = self.bt.sma(period=5)
        self.bt.buy_entry = (fast_ma > slow_ma) & (fast_ma.shift() <= slow_ma.shift())
        self.bt.sell_entry = (fast_ma < slow_ma) & (fast_ma.shift() >= slow_ma.shift())
        self.bt.buy_exit = (self.bt.C < exit_ma) & (
            self.bt.C.shift() >= exit_ma.shift()
        )
        self.bt.sell_exit = (self.bt.C > exit_ma) & (
            self.bt.C.shift() <= exit_ma.shift()
        )

        self.bt.initial_deposit = 100000
        self.bt.stop_loss = 50
        self.bt.units = 10000
        self.bt.take_profit = 100

        actual = self.bt.run()
        expected = 11
        assert expected == len(actual)
