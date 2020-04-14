import os
from oanda_backtest import Backtest
import pytest

import time


@pytest.fixture(scope="module", autouse=True)
def scope_module():
    yield Backtest(
        access_token=os.environ["oanda_backtest_token"], environment="practice"
    )


@pytest.fixture(scope="function", autouse=True)
def bt(scope_module):
    time.sleep(0.5)
    yield scope_module


def test_run_basic(bt):
    bt.candles("EUR_USD")
    fast_ma = bt.sma(period=5)
    slow_ma = bt.sma(period=25)
    bt.sell_exit = bt.buy_entry = (fast_ma > slow_ma) & (
        fast_ma.shift() <= slow_ma.shift()
    )
    bt.buy_exit = bt.sell_entry = (fast_ma < slow_ma) & (
        fast_ma.shift() >= slow_ma.shift()
    )

    actual = bt.run()
    expected = 11
    assert expected == len(actual)


def test_run_advanced(bt):

    filepath = "usd-jpy-h1.csv"
    if bt.exists(filepath):
        bt.read_csv(filepath)
    else:
        bt.candles("USD_JPY", {"granularity": "H1", "count": "5000"})
        bt.to_csv(filepath)

    fast_ma = bt.sma(period=10)
    slow_ma = bt.sma(period=30)
    exit_ma = bt.sma(period=5)
    bt.buy_entry = (fast_ma > slow_ma) & (fast_ma.shift() <= slow_ma.shift())
    bt.sell_entry = (fast_ma < slow_ma) & (fast_ma.shift() >= slow_ma.shift())
    bt.buy_exit = (bt.C < exit_ma) & (bt.C.shift() >= exit_ma.shift())
    bt.sell_exit = (bt.C > exit_ma) & (bt.C.shift() <= exit_ma.shift())

    bt.initial_deposit = 100000
    bt.stop_loss = 50
    bt.units = 10000
    bt.take_profit = 100

    actual = bt.run()
    expected = 11
    assert expected == len(actual)
