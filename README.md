# oanda-backtest

[![PyPI](https://img.shields.io/pypi/v/oanda-backtest)](https://pypi.org/project/oanda-backtest/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![codecov](https://codecov.io/gh/10mohi6/oanda-backtest-python/branch/master/graph/badge.svg)](https://codecov.io/gh/10mohi6/oanda-backtest-python)
[![Build Status](https://travis-ci.com/10mohi6/oanda-backtest-python.svg?branch=master)](https://travis-ci.com/10mohi6/oanda-backtest-python)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/oanda-backtest)](https://pypi.org/project/oanda-backtest/)
[![Downloads](https://pepy.tech/badge/oanda-backtest)](https://pepy.tech/project/oanda-backtest)

oanda-backtest is a python library for backtest with oanda fx trade rest api on Python 3.6 and above.


## Installation

    $ pip install oanda-backtest

## Usage

### basic
```python
from oanda_backtest import Backtest

bt = Backtest(access_token='<your access token>', environment='practice')
bt.candles("EUR_USD")
fast_ma = bt.sma(period=5)
slow_ma = bt.sma(period=25)
bt.sell_exit = bt.buy_entry = (fast_ma > slow_ma) & (fast_ma.shift() <= slow_ma.shift())
bt.buy_exit = bt.sell_entry = (fast_ma < slow_ma) & (fast_ma.shift() >= slow_ma.shift())
bt.run()
bt.plot()
```

### advanced
```python
from oanda_backtest import Backtest

bt = Backtest(access_token='<your access token>', environment='practice')
filepath='usd-jpy-h1.csv'
if bt.exists(filepath):
    bt.read_csv(filepath)
else:
    params = {
        "granularity": "H1",  # 1 hour candlesticks (default=S5)
        "count": 5000 # 5000 candlesticks (default=500, maximum=5000)
    }
    bt.candles("USD_JPY", params)
    bt.to_csv(filepath)

fast_ma = bt.sma(period=10)
slow_ma = bt.sma(period=30)
exit_ma = bt.sma(period=5)
bt.buy_entry = (fast_ma > slow_ma) & (fast_ma.shift() <= slow_ma.shift())
bt.sell_entry = (fast_ma < slow_ma) & (fast_ma.shift() >= slow_ma.shift())
bt.buy_exit = (bt.C < exit_ma) & (bt.C.shift() >= exit_ma.shift())
bt.sell_exit = (bt.C > exit_ma) & (bt.C.shift() <= exit_ma.shift())

bt.initial_deposit = 100000 # default=0
bt.units = 1000 # currency unit (default=10000)
bt.stop_loss = 50 # stop loss pips (default=0)
bt.take_profit = 100 # take profit pips (default=0)

print(bt.run())
bt.plot("backtest.png")

```

```python
total profit        1989.000
total trades         171.000
win rate              35.088
profit factor          1.198
maximum drawdown    2745.000
recovery factor        0.725
riskreward ratio       2.236
sharpe ratio           0.050
average return        10.666
stop loss              5.000
take profit            5.000
```
![advanced.png](https://raw.githubusercontent.com/10mohi6/oanda-backtest-python/master/tests/advanced.png)


## Supported indicators
- Simple Moving Average 'sma'
- Exponential Moving Average 'ema'
- Moving Average Convergence Divergence 'macd'
- Relative Strenght Index 'rsi'
- Bollinger Bands 'bband'
- Stochastic Oscillator 'stoch'
- Market Momentum 'mom'


## Getting started

For help getting started with OANDA REST API, view our online [documentation](https://developer.oanda.com/rest-live-v20/introduction/).


## Contributing

1. Fork it
2. Create your feature branch (`git checkout -b my-new-feature`)
3. Commit your changes (`git commit -am 'Add some feature'`)
4. Push to the branch (`git push origin my-new-feature`)
5. Create new Pull Request