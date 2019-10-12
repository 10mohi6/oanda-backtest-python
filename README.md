# oanda-backtest

[![PyPI](https://img.shields.io/pypi/v/oanda-backtest)](https://pypi.org/project/oanda-backtest/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![codecov](https://codecov.io/gh/10mohi6/oanda-backtest-python/branch/master/graph/badge.svg)](https://codecov.io/gh/10mohi6/oanda-backtest-python)
[![Build Status](https://travis-ci.com/10mohi6/oanda-backtest-python.svg?branch=master)](https://travis-ci.com/10mohi6/oanda-backtest-python)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/oanda-backtest)](https://pypi.org/project/oanda-backtest/)

oanda-backtest is a python library for backtest with oanda rest api on Python 3.5 and above.


## Installation

    $ pip install oanda-backtest

## Usage

```python
#
# basic
#
from oanda_backtest import Backtest

bt = Backtest(token='XXXXXXXXXX')
bt.get("EUR_USD")
fast_ma = bt.sma(period=5)
slow_ma = bt.sma(period=25)
bt.sell_exit = bt.buy_entry = ((fast_ma > slow_ma) & (fast_ma.shift() <= slow_ma.shift())).values
bt.buy_exit = bt.sell_entry = ((fast_ma < slow_ma) & (fast_ma.shift() >= slow_ma.shift())).values
bt.run()
bt.plot()

#
# advanced
#
from oanda_backtest import Backtest
import os

bt = Backtest(token='XXXXXXXXXX')
filepath='usd-jpy-h1.csv'
if os.path.exists(filepath):
    df = bt.read_csv(filepath)
else:
    params = {
        "granularity": "H1",  # 1 hour candlesticks
        "count": 5000 # 5000 candlesticks (default=500, maximum=5000)
    }
    df = bt.get("USD_JPY", params)
    bt.to_csv(filepath)

fast_ma = bt.sma(period=10)
slow_ma = bt.sma(period=30)
exit_ma = bt.sma(period=5)
bt.buy_entry = ((fast_ma > slow_ma) & (fast_ma.shift() <= slow_ma.shift())).values
bt.sell_entry = ((fast_ma < slow_ma) & (fast_ma.shift() >= slow_ma.shift())).values
bt.buy_exit = ((bt.C < exit_ma) & (bt.C.shift() >= exit_ma.shift())).values
bt.sell_exit = ((bt.C > exit_ma) & (bt.C.shift() <= exit_ma.shift())).values

bt.initial_deposit = 100000 # default=0
bt.point = 0.01 # 1pips (default=0.0001)
bt.lots = 1000 # currency unit (default=10000)
bt.loss_cut = 50 # loss cut pips (default=0)
bt.profit_taking = 100 # profit taking pips (default=0)

print(bt.run())
bt.plot("backtest.png")

```

```python
total profit            72.00
total trades           188.00
win rate                29.79
profit factor            1.01
maximum drawdown      2781.00
recovery factor          0.03
riskreward ratio         2.36
sharpe ratio             0.00
average return           0.17
loss cut rate            0.53
profit taking rate       0.53
```
![backtest.png](https://github.com/10mohi6/oanda-backtest-python/tree/master/tests/backtest.png)


## Getting started

For help getting started with OANDA REST API, view our online [documentation](https://developer.oanda.com/rest-live-v20/introduction/).


## Contributing

1. Fork it
2. Create your feature branch (`git checkout -b my-new-feature`)
3. Commit your changes (`git commit -am 'Add some feature'`)
4. Push to the branch (`git push origin my-new-feature`)
5. Create new Pull Request