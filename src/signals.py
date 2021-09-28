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

# Tendencia
# [X] SMA
# [x] MACD
# [X] ADX - https://www.backtrader.com/docu/indautoref/#averagedirectionalmovementindexrating

# Moment/ Osciladores
# [X] RSI
# [X] Williams R
# [X] Stochastic Oscilator - https://www.backtrader.com/docu/indautoref/#stochasticfull

# Volatilidade
# [X] ATR (Média de Amplitude de Variação)
# [X] Bandas de Bollinger - https://www.backtrader.com/docu/indautoref/#bollingerbandspct

# Volume
# [ ] OBV (Saldo de Volume) - https://www.backtrader.com/docu/talibindautoref/#obv
# [ ] FI (Force index) - https://community.backtrader.com/topic/3039/elders-force-index


class TIMESignal(bt.Indicator):
    lines = (('signal'),)

    params = (('time_start', [9, 0]),
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


# Volatilidade/STOP
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
              ('atrdist', 2.),  # ATR distance for stop price
              ('atrprofit', 2.),  # ATR ratio for takeprofit
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


# Tendencia
class SMASignal(bt.Indicator):
    lines = (('sma'),
             ('signal'))
    params = (('period_sma', 25),
              )
    # plotinfo = dict(subplot=False)
    plotinfo = dict(subplot=True)

    def __init__(self, **kwargs):
        # self.__dict__.update(kwargs)
        allowed_keys = {'period_sma'}
        self.params.__dict__.update((k, v) for k, v in kwargs.items() if k in allowed_keys)
        self.params.__dict__.update({"analyzer_opt": kwargs.get("analyzer_opt")})

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


# Tendencia
class MACDSignal(bt.Indicator):
    lines = (('macd'),
             ('signal'),
             ('histo'))
    params = {'period_me1': 12,
              'period_me2': 26,
              'period_signal': 9,
              # 'movav': 'ExponentialMovingAverage', #will not be updated so don't need to declare it here
              }
    plotinfo = dict(subplot=False)
    # plotinfo = dict(subplot=True)

    def __init__(self, **kwargs):
        # self.__dict__.update(kwargs)
        allowed_keys = ['period_me1', 'period_me2', 'period_signal']
        self.params.__dict__.update((k, v) for k, v in kwargs.items() if k in allowed_keys)
        self.params.__dict__.update({"analyzer_opt": kwargs.get("analyzer_opt")})

        # me1 = self.params.movav(self.data, period=self.params.period_me1)
        # me2 = self.params.movav(self.data, period=self.params.period_me2)
        # self.lines.macd = me1 - me2
        # self.lines.signal = self.params.movav(self.lines.macd, period=self.params.period_signal)
        # self.lines.histo = self.lines.macd - self.lines.signal

        # self.macd = bt.indicators.MACD(
        #     self.datas[0], period_me1=12, period_me2=26, period_signal=9)
        # self.macdhisto = bt.indicators.MACDHisto(
        #     self.datas[0], period_me1=12, period_me2=26, period_signal=9)
        self.lines.signal = bt.indicators.MACD(
            self.datas[0], period_me1=self.params.period_me1, period_me2=self.params.period_me2, period_signal=self.params.period_signal)
        self.lines.histo = bt.indicators.MACDHisto(
            self.datas[0], period_me1=self.params.period_me1, period_me2=self.params.period_me2, period_signal=self.params.period_signal)

    def next(self):
        if self.lines.signal[0] > 0:
            self.lines.signal[0] = 100
        elif self.lines.signal[0] < 0:
            self.lines.signal[0] = -100
        else:
            self.lines.signal[0] = 0.0


# Tendencia
class ADXSignal(bt.Indicator):
    lines = (('adx'),
             ('adxr'),
             ('signal'))
    params = {'period_adx': 14,
              'period_adxr': 10,
              # 'movav': 'SmoothedMovingAverage', #will not be updated so don't need to declare it here
              }
    plotinfo = dict(subplot=False)
    # plotinfo = dict(subplot=True)

    def __init__(self, **kwargs):
        # self.__dict__.update(kwargs)
        allowed_keys = ['period_adx', 'period_adxr']
        self.params.__dict__.update((k, v) for k, v in kwargs.items() if k in allowed_keys)
        self.params.__dict__.update({"analyzer_opt": kwargs.get("analyzer_opt")})

        self.adx = bt.indicators.AverageDirectionalMovementIndex(period=self.params.period_adx)
        self.adxr = bt.indicators.AverageDirectionalMovementIndexRating(period=self.params.period_adxr)

        self.lines.adx = self.adxr.lines.adx
        self.lines.adxr = self.adxr.lines.adxr

    def next(self):
        if (self.lines.adx[0] > 25) & (self.lines.adx[0] > self.lines.adxr[0]):
            self.lines.signal[0] = 100
        elif (self.lines.adx[0] > 25) & (self.lines.adx[0] < self.lines.adxr[0]):
            self.lines.signal[0] = -100
        else:
            self.lines.signal[0] = 0.0


# Moment/ Osciladores
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
        self.params.__dict__.update({"analyzer_opt": kwargs.get("analyzer_opt")})

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


# Moment/ Osciladores
# class WillRSignal(bt.Indicator):
#     """WilliamsR
#     Developed by Larry Williams to show the relation of closing prices to the highest-lowest range of a given period.
#
#     Known as Williams %R (but % is not allowed in Python identifiers)
#
#     Formula:
#     num = highest_period - close
#     den = highestg_period - lowest_period
#     percR = (num / den) * -100.0
#
#     See:
#
#     http://en.wikipedia.org/wiki/Williams_%25R
#
#     Lines:
#     percR
#
#     Params:
#     period (14)
#     upperband (-20.0)
#     lowerband (-80.0)
#
#     PlotInfo:
#     plot (True)
#     plotmaster (None)
#     legendloc (None)
#     subplot (True)
#     plotname (Williams R%)
#     plotskip (False)
#     plotabove (False)
#     plotlinelabels (False)
#     plotlinevalues (True)
#     plotvaluetags (True)
#     plotymargin (0.0)
#     plotyhlines ([])
#     plotyticks ([])
#     plothlines ([])
#     plotforce (False)
#
#     PlotLines:
#     percR:
#
#     _name (R%)
#
#     """
#     lines = (('willr'),
#              ('signal'),
#              )
#     params = (('period_willr', 3),
#               ('threshold_upper', -20),
#               ('threshold_lower', -80),
#               )
#     # plotinfo = dict(subplot=False)
#
#     def __init__(self, **kwargs):
#         # self.__dict__.update(kwargs)
#         allowed_keys = {'period_willr', 'threshold_upper', 'threshold_lower'}
#         self.params.__dict__.update((k, v) for k, v in kwargs.items() if k in allowed_keys)
#         self.params.__dict__.update({"analyzer_opt": kwargs.get("analyzer_opt")})
#
#         self.willr = bt.indicators.WilliamsR(period=self.params.period_willr,
#                                              upperband=self.params.threshold_upper,
#                                              lowerband=self.params.threshold_lower)
#         self.lines.willr = self.willr
#         self.threshold_buy = self.params.threshold_lower
#         self.threshold_sell = self.params.threshold_upper
#
#         # to show date/time progress
#         # self.trace = 0
#
#     def next(self):
#         if self.lines.willr[0] > self.threshold_buy:
#             self.lines.signal[0] = 100
#         elif self.lines.willr[0] < self.threshold_sell:
#             self.lines.signal[0] = -100
#         else:
#             self.lines.signal[0] = 0.0
#
#
# # Moment/ Osciladores
# class StochasticSignal(bt.Indicator):
#     lines = (('percK'),
#              ('percD'),
#              ('percDSlow'),
#              ('signal'))
#     params = {'period_dslow': 3,
#               'period_dfast': 3,
#               'period': 14,
#               'upperband': 80.0,
#               'lowerband': 20.0,
#               # 'movav': 'MovingAverage', #will not be updated so don't need to declare it here
#               }
#     plotinfo = dict(subplot=False)
#
#     def __init__(self, **kwargs):
#         # self.__dict__.update(kwargs)
#         allowed_keys = {'period_dslow', 'period_dfast', 'period', 'upperband', 'lowerband'}
#         self.params.__dict__.update((k, v) for k, v in kwargs.items() if k in allowed_keys)
#         self.params.__dict__.update({"analyzer_opt": kwargs.get("analyzer_opt")})
#
#         self.stoch = bt.indicators.StochasticFull(period=self.params.period,
#                                                   period_dslow=self.params.period_dslow,
#                                                   period_dfast=self.params.period_dfast,
#                                                   upperband=self.params.upperband,
#                                                   lowerband=self.params.lowerband
#                                                   )
#
#     def next(self):
#         if self.stoch.lines.percDSlow[0] > self.params.upperband:
#             self.lines.signal[0] = 100
#         elif self.stoch.lines.percDSlow[0] < self.params.lowerband:
#             self.lines.signal[0] = -100
#         else:
#             self.lines.signal[0] = 0.0


# Volatilidade
# class BollingerBandsSignal(bt.indicators):
#     lines = (('mid'),
#              ('top'),
#              ('bot'),
#              ('pctb'),
#              ('signal'))
#     params = {'period': 20,
#               'devfactor': 2,
#               # 'movav': 'MovingAverage', #will not be updated so don't need to declare it here
#               }
#     plotinfo = dict(subplot=False)
#
#     def __init__(self):
#         self.lines.pctb = bt.indicators.BollingerBandsPct(period=self.params.period)
#
#     def next(self):
#         if self.lines.pctb > 1:
#             self.lines.signal[0] = 100
#         elif self.lines.pctb < 1:
#             self.lines.signal[0] = -100
#         else:
#             self.lines.signal[0] = 0.0



# Volume
# class OBVSignal(bt.Indicator):
#     '''
#     REQUIREMENTS
#     ----------------------------------------------------------------------
#     Investopedia:
#     ----------------------------------------------------------------------
#     https://stockcharts.com/school/doku.php?id=chart_school:technical_indicators:on_balance_volume_obv
#     https://backtest-rookies.com/2018/11/30/backtrader-on-balance-volume/
#
#     1. If today's closing price is higher than yesterday's closing price,
#        then: Current OBV = Previous OBV + today's volume
#
#     2. If today's closing price is lower than yesterday's closing price,
#        then: Current OBV = Previous OBV - today's volume
#
#     3. If today's closing price equals yesterday's closing price,
#        then: Current OBV = Previous OBV
#     ----------------------------------------------------------------------
#     '''
#     alias = 'OBV'
#     lines = (('obv'),
#              ('signal'))
#     params = (('period_obv', 25),
#               )
#     plotlines = dict(
#         obv=dict(
#             _name='OBV',
#             color='purple',
#             alpha=0.50
#         ))
#     plotinfo = dict(subplot=False)
#     # plotinfo = dict(subplot=True)
#
#     def __init__(self, **kwargs):
#         self.vol = self.data.volume
#         self.lines.obv = bt.If(self.data.close(0) > self.data.close(-1),
#                                (self.vol + self.data.volume),
#                                self.vol - self.data.volume)
#
#     def nextstart(self):
#         # We need to use next start to provide the initial value. This is because
#         # we do not have a previous value for the first calculation. These are
#         # known as seed values.
#
#         # Create some aliases
#         c = self.data.close
#         v = self.data.volume
#         obv = self.lines.obv
#
#         if c[0] > c[-1]:
#             obv[0] = v[0]
#         elif c[0] < c[-1]:
#             obv[0] = -v[0]
#         else:
#             obv[0] = 0
#
#     def next(self):
#         # Aliases to avoid long lines
#         c = self.data.close
#         v = self.data.volume
#         obv = self.lines.obv
#         if c[0] > c[-1]:
#             obv[0] = obv[-1] + v[0]
#         elif c[0] < c[-1]:
#             obv[0] = obv[-1] - v[0]
#         else:
#             obv[0] = obv[-1]


# Volume

# Moment/ Osciladores
class ElderForceIndexSignal(bt.Indicator):
    lines = (('efi1'),
             ('efi2'),
             ('signal'),
             )
    params = (('period_ema1', 2),
              ('period_ema2', 13),
              )
    # plotinfo = dict(subplot=False)

    def __init__(self, **kwargs):
        # self.__dict__.update(kwargs)
        allowed_keys = {'period_rsi', 'threshold_buy', 'threshold_sell'}
        self.params.__dict__.update((k, v) for k, v in kwargs.items() if k in allowed_keys)
        self.params.__dict__.update({"analyzer_opt": kwargs.get("analyzer_opt")})

        self.lines.efi1 = bt.indicators.ExponentialMovingAverage(
            self.datas[0].volume(0) * (self.datas[0].close(0) - self.datas[0].close(-1)),
            period=self.params.period_ema1)
        self.lines.efi2 = bt.indicators.ExponentialMovingAverage(
            self.datas[0].volume(0) * (self.datas[0].close(0) - self.datas[0].close(-1)),
            period=self.params.period_ema2)

    def next(self):
        if (self.lines.efi2[0] >= 0):
            if (self.lines.efi1[0] > 0) & (self.lines.efi1[0] > self.lines.efi2[0]):
                self.lines.signal[0] = 100
            else:
                self.lines.signal[0] = 0
        elif (self.lines.efi2[0] < 0):
            if (self.lines.efi1[0] < 0) & (self.lines.efi1[0] < self.lines.efi2[0]):
                self.lines.signal[0] = -100
            else:
                self.lines.signal[0] = 0




# class GenericSignal(bt.Indicator):
#     lines = (('signal'),
#              ('atr'),
#              ('signal_stopbuy'),
#              ('signal_stopsell'),
#              ('signal_takeprofit'),
#              ('signal_profit_buy'),
#              ('signal_profit_sell'),
#              )
#     params = ()
#     # plotinfo = dict(subplot=False)
#
#     def __init__(self, **kwargs):
#         # self.__dict__.update(kwargs)
#         self.params.__dict__.update(kwargs)     # nem precisaria
#         # allowed_keys = {'period_rsi', 'threshold_buy', 'threshold_sell'}
#         # self.params.__dict__.update((k, v) for k, v in kwargs.items() if k in allowed_keys)
#
#         # signal = self.params.signal
#         signal = kwargs["signal"]
#         self.lines.signal = globals()[signal](**kwargs)
#
#         self.lines.atr = ATRSignal(**kwargs)
#
#         # self.lines.signal_takeprofit = self.lines.atr.lines
#         # self.lines.signal_stopbuy = self.data - self.lines.signal
#         # self.lines.signal_stopsell = self.data + self.lines.signal
#         # self.lines.signal_profit_buy = self.data + self.lines.signal_takeprofit
#         # self.lines.signal_profit_sell = self.data - self.lines.signal_takeprofit



