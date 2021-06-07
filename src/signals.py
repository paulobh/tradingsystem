from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import collections
import datetime
import backtrader as bt


MAINSIGNALS = collections.OrderedDict(
    (('longshort', bt.SIGNAL_LONGSHORT),
     ('longonly', bt.SIGNAL_LONG),
     ('shortonly', bt.SIGNAL_SHORT),)
)

EXITSIGNALS = {
    'longexit': bt.SIGNAL_LONGEXIT,
    'shortexit': bt.SIGNAL_LONGEXIT,
}


class ATRSignal(bt.Indicator):
    lines = (('atr'),
             ('signal'),
             ('signal_stopbuy'),
             ('signal_stopsell'),
             ('signal_takeprofit'),
             ('signal_profit_buy'),
             ('signal_profit_sell'),
             )
    params = (('period_atr', 20),
              ('atrdist', 1.5),  # ATR distance for stop price
              ('atrprofit', 1.5),  # ATR ratio for takeprofit
              )
    plotinfo = dict(subplot=False)

    def __init__(self, **kwargs):
        # self.__dict__.update(kwargs)
        allowed_keys = {'period_atr', 'atrdist', 'atrprofit'}
        self.params.__dict__.update((k, v) for k, v in kwargs.items() if k in allowed_keys)

        self.atr = bt.indicators.AverageTrueRange(period=self.params.period_atr)

        self.lines.signal = self.atr * self.params.atrdist // 1
        self.lines.signal_takeprofit = self.lines.signal * self.params.atrprofit // 1

        self.lines.signal_stopbuy = self.data - self.lines.signal
        self.lines.signal_stopsell = self.data + self.lines.signal

        self.lines.signal_profit_buy = self.data + self.lines.signal_takeprofit
        self.lines.signal_profit_sell = self.data - self.lines.signal_takeprofit


class RSISignal(bt.Indicator):
    """RelativeStrengthIndex
    Alias: RSI, RSI_SMMA, RSI_Wilder
    Defined by J. Welles Wilder, Jr. in 1978 in his book “New Concepts in Technical Trading Systems”.

    It measures momentum by calculating the ration of higher closes and lower closes after having been smoothed by an average, normalizing the result between 0 and 100

    Formula:
    up = upday(data)
    down = downday(data)
    maup = movingaverage(up, period)
    madown = movingaverage(down, period)
    rs = maup / madown

    rsi = 100 - 100 / (1 + rs)

    The moving average used is the one originally defined by Wilder, the SmoothedMovingAverage

    See: http://en.wikipedia.org/wiki/Relative_strength_index

    #Notes:
    safediv (default: False) If this parameter is True the division rs = maup / madown will be checked for the special cases in which a 0 / 0 or x / 0 division will happen
    safehigh (default: 100.0) will be used as RSI value for the x / 0 case
    safelow (default: 50.0) will be used as RSI value for the 0 / 0 case

    #Lines:
    rsi

    #Params:
    period (14)
    movav (SmoothedMovingAverage)
    upperband (70.0)
    lowerband (30.0)
    safediv (False)
    safehigh (100.0)
    safelow (50.0)
    lookback (1)

    #PlotInfo:
    plot (True)
    plotmaster (None)
    legendloc (None)
    subplot (True)
    plotname ()
    plotskip (False)
    plotabove (False)
    plotlinelabels (False)
    plotlinevalues (True)
    plotvaluetags (True)
    plotymargin (0.0)
    plotyhlines ([])
    plotyticks ([])
    plothlines ([])
    plotforce (False)

    #PlotLines:
    rsi:

    #Signal
    Lines:

    signal
    PlotInfo:

    plot (True)
    plotmaster (None)
    legendloc (None)
    subplot (True)
    plotname ()
    plotskip (False)
    plotabove (False)
    plotlinelabels (False)
    plotlinevalues (True)
    plotvaluetags (True)
    plotymargin (0.0)
    plotyhlines ([])
    plotyticks ([])
    plothlines ([])
    plotforce (False)

    PlotLines:
    signal:

    """
    lines = (('rsi'),
             ('signal'),
             )
    params = (('period_rsi', 25),
              ('threshold_buy', 30),
              ('threshold_sell', 70),
              )
    # plotinfo = dict(subplot=False)

    def __init__(self, **kwargs):
        # self.__dict__.update(kwargs)
        allowed_keys = {'period_rsi', 'threshold_buy', 'threshold_sell'}
        self.params.__dict__.update((k, v) for k, v in kwargs.items() if k in allowed_keys)

        self.rsi = bt.indicators.RelativeStrengthIndex(period=self.params.period_rsi,
                                                       safediv=True)
        self.lines.rsi = self.rsi

        self.threshold_buy = self.params.threshold_buy
        self.threshold_sell = self.params.threshold_sell

    def next(self):
        if self.rsi[0] < self.threshold_buy:
            self.lines.signal[0] = 100
        elif self.rsi[0] > self.threshold_sell:
            self.lines.signal[0] = -100
        else:
            self.lines.signal[0] = 0.0


class WillRSignal(bt.Indicator):
    """WilliamsR
    Developed by Larry Williams to show the relation of closing prices to the highest-lowest range of a given period.

    Known as Williams %R (but % is not allowed in Python identifiers)

    Formula:
    num = highest_period - close
    den = highestg_period - lowest_period
    percR = (num / den) * -100.0

    See:

    http://en.wikipedia.org/wiki/Williams_%25R

    Lines:
    percR

    Params:
    period (14)
    upperband (-20.0)
    lowerband (-80.0)

    PlotInfo:
    plot (True)
    plotmaster (None)
    legendloc (None)
    subplot (True)
    plotname (Williams R%)
    plotskip (False)
    plotabove (False)
    plotlinelabels (False)
    plotlinevalues (True)
    plotvaluetags (True)
    plotymargin (0.0)
    plotyhlines ([])
    plotyticks ([])
    plothlines ([])
    plotforce (False)

    PlotLines:
    percR:

    _name (R%)

    """
    lines = (('willr'),
             ('signal'),
             )
    params = (('period_willr', 3),
              ('threshold_upper', -20),
              ('threshold_lower', -80),
              )
    # plotinfo = dict(subplot=False)

    def __init__(self, **kwargs):
        # self.__dict__.update(kwargs)
        allowed_keys = {'period_willr', 'threshold_upper', 'threshold_lower'}
        self.params.__dict__.update((k, v) for k, v in kwargs.items() if k in allowed_keys)

        self.willr = bt.indicators.WilliamsR(period=self.params.period_willr,
                                             upperband=self.params.threshold_upper,
                                             lowerband=self.params.threshold_lower)
        self.lines.willr = self.willr
        self.threshold_buy = self.params.threshold_lower
        self.threshold_sell = self.params.threshold_upper

        # to show date/time progress
        # self.trace = 0

    def next(self):
        if self.lines.willr > self.threshold_buy:
            self.lines.signal[0] = 100
        elif self.lines.willr < self.threshold_sell:
            self.lines.signal[0] = -100
        else:
            self.lines.signal[0] = 0.0


class TIMESignal(bt.Indicator):
    lines = (('signal'),)

    params = (('time_start', [9, 30]),
              ('time_stop', [17, 0]),
              )
    # plotinfo = dict(subplot=False)

    def __init__(self, **kwargs):
        # self.__dict__.update(kwargs)
        allowed_keys = {'time_start', 'time_stop'}
        self.params.__dict__.update((k, v) for k, v in kwargs.items() if k in allowed_keys)

        self.time_stop = datetime.time(*self.params.time_stop)
        self.time_start = datetime.time(*self.params.time_start)

    def next(self):
        self.time = self.data.datetime.time()
        if (self.time > self.time_start) & (self.time < self.time_stop):
            self.lines.signal[0] = 1
        else:
            self.lines.signal[0] = 0


class SMASignal(bt.Indicator):
    lines = (('sma'),
             ('signal'),
             )
    params = (('period_sma', 25),
              )
    # plotinfo = dict(subplot=False)
    plotinfo = dict(subplot=True)

    def __init__(self, **kwargs):
        # self.__dict__.update(kwargs)
        allowed_keys = {'period_sma'}
        self.params.__dict__.update((k, v) for k, v in kwargs.items() if k in allowed_keys)

        # Add a MovingAverageSimple indicator
        # self.sma = bt.indicators.MovingAverageSimple(self.datas[0],
        self.sma = bt.indicators.MovingAverageSimple(period=self.params.period_sma)
        # print(f"sma period used: {self.params.period_sma}")
        self.lines.sma = self.sma

        # # Keep a reference to the "close" line in the data[0] dataseries
        self.dataclose = self.datas[0].close    # ja foi definido na estratégia

    def next(self):
        if self.dataclose[0] > self.sma[0]:
            self.lines.signal[0] = 100
        elif self.dataclose[0] < self.sma[0]:
            self.lines.signal[0] = -100
        else:
            self.lines.signal[0] = 0.0
