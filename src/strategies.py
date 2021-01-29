from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import argparse
import collections
import datetime
import numpy

# Import the backtrader platform
import backtrader as bt

from args import parse_args


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
    args = parse_args()

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

    def __init__(self):
        self.atr = bt.indicators.AverageTrueRange(period=self.params.period_atr)
        self.lines.signal = self.atr * self.params.atrdist // 1
        self.lines.signal_stopbuy = self.data - self.lines.signal
        self.lines.signal_stopsell = self.data + self.lines.signal
        self.lines.signal_takeprofit = self.lines.signal * self.params.atrprofit // 1
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
    args = parse_args()

    lines = (('rsi'),
             ('signal'),
             # ('signal_buy'),
             # ('signal_sell'),
             )
    params = (('period_rsi', 20),
              ('threshold_buy', 30),
              ('threshold_sell', 70),
              ('target', 400),
              )
    # plotinfo = dict(subplot=False)

    def __init__(self):
        self.rsi = bt.indicators.RelativeStrengthIndex(period=self.params.period_rsi,
                                                       safediv=True)
        self.threshold_buy = self.params.threshold_buy
        self.threshold_sell = self.params.threshold_sell

        self.lines.rsi = self.rsi
        # self.lines.signal_buy = self.threshold_buy - self.rsi
        # self.lines.signal_sell = self.rsi - self.threshold_sell

        # to show date/time progress
        # self.trace = 0

    def next(self):
        # if (self.threshold_buy - self.rsi[0]) > 0:
        if self.rsi[0] < self.threshold_buy:
            self.lines.signal[0] = 100
        # elif (self.rsi[0] - self.threshold_sell) > 0:
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
    args = parse_args()

    lines = (('willr'),
             ('signal'),
             # ('signal_buy'),
             # ('signal_sell'),
             )
    params = (('period_willr', 3),
              ('threshold_upper', -20),
              ('threshold_lower', -80),
              # ('target', 400),
              )
    # plotinfo = dict(subplot=False)

    def __init__(self):
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
    args = parse_args()

    lines = (('signal'),)

    params = (('time_start', [10, 0]),
              ('time_stop', [16, 45]),
              )

    def __init__(self):
        # self.time = self.datas[0].datetime
        self.time_stop = datetime.time(self.params.time_stop[0], self.params.time_stop[1])
        self.time_start = datetime.time(self.params.time_start[0], self.params.time_start[1])

    def next(self):
        if (self.data.datetime.time() > self.time_start) & (self.data.datetime.time() < self.time_stop):
            self.lines.signal[0] = 1
        else:
            self.lines.signal[0] = 0


# Create a Stratey
class TestStrategy(bt.Strategy):

    def log(self, txt, dt=None):
        ''' Logging function for this strategy'''
        # dt = dt or self.datas[0].datetime.date(0)
        dt = dt or self.datas[0].datetime.datetime(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        # self.atr = ATRSignal()
        # self.rsi = RSISignal()
        self.time_signal = TIMESignal()
        # Keep a reference to the OHLC line in the data[0] dataseries
        self.dataopen = self.datas[0].open
        self.datahigh = self.datas[0].high
        self.datalow = self.datas[0].low
        self.dataclose = self.datas[0].close

    def next(self):
        # Simply log the closing price of the series from the reference
        # self.log('Close, %.2f' % self.dataclose[0])
        # self.log('ATR, %.2f' % self.atr.signal[0])
        # self.log('ATR_sig, %.2f' % self.atr.signal_atr[0])
        # self.log('RSI, %.2f' % self.rsi.signal_buy[0])
        self.log('Datetime: %s, Open: %.2f, High: %.2f, Low: %.2f, Close: %.2f' %
                 (self.data.datetime.datetime(0),
                  self.dataopen[0],
                  self.datahigh[0],
                  self.datalow[0],
                  self.dataclose[0])
                 )
        # self.log('Datetime: %s, ATR: %.2f, ATR_stopbuy: %.2f, ATR_stopsell: %.2f' %
        #          (self.data.datetime.datetime(0),
        #           self.atr.signal[0],
        #           self.atr.signal_stopbuy[0],
        #           self.atr.signal_stopsell[0])
        #          )


class MainStrategy(bt.Strategy):
    args = parse_args()

    params = (('plot_entry', True),
              ('plot_exit', True),
              # ('use_target_size', False),
              # ('use_target_value', False),
              # ('use_target_percent', False),
              # ('trailamount', 0.0),
              # ('trailpercent', 0.0),
              # ('hold', 10),     #number of candles to close order (just for testing)
              ('limdays', 1),   #limit of days of alive orders
              )

    def log(self, txt, dt=None):
        """Logging function for this strategy"""
        # dt = dt or self.datas[0].datetime.date(0)
        dt = dt or self.datas[0].datetime.datetime(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):

        # To keep track of pending orders and buy price / commission.
        self.order = None
        # self.orderprice = None
        # self.commission = None
        # self.orderstop = None
        # self.pdist = None

        # Keep a reference to the OHLC line in the data[0] dataseries
        self.dataopen = self.datas[0].open
        self.datahigh = self.datas[0].high
        self.datalow = self.datas[0].low
        self.dataclose = self.datas[0].close

        self.atr = ATRSignal()
        self.rsi = RSISignal()
        self.willr = WillRSignal()

        self.price_at_signal = 0
        self.trades = 0
        # self.orefs = list()

    def start(self):
        self.trades = 0

    def notify_trade(self, trade):
        """Receives a trade whenever there has been a change in one"""
        if not trade.isclosed:
            return

        self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' %
                 (trade.pnl, trade.pnlcomm))

    def notify_order(self, order):
        """Receives an order whenever there has been a change in one"""

        # Check whether an order has enought Margin to call or was Rejected by the Broker
        if order.status in [order.Margin, order.Rejected]:
            print('Order Margin/Rejected')
            pass

        # Check whether an order is Submitted or Accepted by the Broker
        if order.status in [order.Submitted, order.Accepted]:
            # Order accepted by the broker. Do nothing.
            # print('Order Submitted/Accepted')
            return

        elif order.status in [order.Cancelled]:
            # self.log(' '.join(map(str, [
            #     'CANCEL ORDER. Type :', order.info['name'], "/ DATE :",
            #     self.data.num2date(order.executed.dt).date().isoformat(),
            #     "/ PRICE :",
            #     order.executed.price,
            #     "/ SIZE :",
            #     order.executed.size,
            # ])))

            # self.log('CANCEL ORDER. Type: %s, Datetime: %s, PRICE: %.2f, SIZE: %.2f' %
            self.log('CANCEL ORDER. Type: %s, PRICE: %.2f, SIZE: %.2f' %
                     (order.info['name'],
                      # self.data.num2date(order.executed.dt),
                      # self.data.datetime.datetime(0),
                      order.executed.price,
                      order.executed.size)
                     )

        # Check if an order is completed
        elif order.status in [order.Completed]:
            # If a stop loss or take profit is triggered:
            if 'name' in order.info:
                self.log("%s: REF : %s PRICE : %.3f SIZE : %.2f COMM : %.2f" %
                         (order.info['name'], order.ref,
                          # self.data.num2date(order.executed.dt).date().isoformat(),
                          order.executed.price,
                          order.executed.size,
                          order.executed.comm))

            else:
                if order.isbuy():
                    # print('Buy Executed Price: %.2f, Cost : %.2f, Commission : %.2f' %
                    # print('Buy Executed Price: %.2f, Cost : %.2f, Stop : %.2f' %
                    # print('Buy Executed Price: %.2f, Cost : %.2f' %
                    #       (order.executed.price,
                    #        order.executed.value
                    #        # self.pstop
                    #        ))
                    # self.orderprice = order.executed.price
                    # self.orderstop = self.pstop

                    # Initialize our take profit and stop loss orders
                    # stop_loss = self.atr.lines.signal[0]
                    # stop_loss = self.atr.lines.signal_stopbuy[0]
                    # take_profit = self.rsi.params.target

                    stop_loss = order.executed.price - self.atr.lines.signal[0]
                    take_profit = order.executed.price + self.rsi.params.target

                    stop_order = self.sell(exectype=bt.Order.Limit,
                                            # exectype=bt.Order.StopLimit,
                                           price=stop_loss,
                                           # valid=datetime.timedelta(self.params.limdays)
                                           )
                    stop_order.addinfo(name="STOP")

                    # OCO : One cancels the Other => The execution of one instantaneously cancels the other
                    takeprofit_order = self.sell(exectype=bt.Order.Limit,
                                                 price=take_profit,
                                                 oco=stop_order,
                                                 # valid=datetime.timedelta(self.params.limdays)
                                                 )
                    takeprofit_order.addinfo(name="PROFIT")

                    self.log("SignalPrice : %.3f Buy: %.3f, Stop: %.3f, Profit : %.3f"
                             % (self.price_at_signal,
                                order.executed.price,
                                stop_loss,
                                take_profit))

                elif order.issell():
                    # print('Sell Executed Price: %.2f, Cost : %.2f, Commission : %.2f' %
                    # print('Sell Executed Price: %.2f, Cost : %.2f, Stop : %.2f' %
                    # print('Sell Executed Price: %.2f, Cost : %.2f' %
                    #       (order.executed.price,
                    #        order.executed.value
                    #        # self.pstop
                    #        ))
                    # self.orderprice = order.executed.price
                    # self.orderstop = self.pstop

                    # Initialize our take profit and stop loss orders
                    # stop_loss = self.atr.lines.signal[0]
                    # stop_loss = self.atr.lines.signal_stopsell[0]
                    # take_profit = self.rsi.params.target

                    stop_loss = order.executed.price + self.atr.lines.signal[0]
                    take_profit = order.executed.price - self.rsi.params.target

                    stop_order = self.buy(exectype=bt.Order.Limit,
                                            # exectype=bt.Order.StopLimit,
                                           price=stop_loss,
                                           # valid=datetime.timedelta(self.params.limdays)
                                           )
                    stop_order.addinfo(name="STOP")

                    # OCO : One cancels the Other => The execution of one instantaneously cancels the other
                    takeprofit_order = self.buy(exectype=bt.Order.Limit,
                                                 price=take_profit,
                                                 oco=stop_order,
                                                 # valid=datetime.timedelta(self.params.limdays)
                                                 )
                    takeprofit_order.addinfo(name="PROFIT")

                    self.log("SignalPrice : %.3f Sell: %.3f, Stop: %.3f, Profit : %.3f"
                             % (self.price_at_signal,
                                order.executed.price,
                                stop_loss,
                                take_profit))

            # self.bar_executed = len(self)

        # self.order = None
        # if not order.alive():
        #     self.order = None  # indicate no order is pending

    def next(self):
        """Simply log the closing price of the series from the reference"""

        print('Datetime: %s, Open: %.2f, High: %.2f, Low: %.2f, Close: %.2f' %
              (self.data.datetime.datetime(0),
               self.dataopen[0],
               self.datahigh[0],
               self.datalow[0],
               self.dataclose[0])
              )

        # print('Datetime: %s, ATR: %.2f, RSI: %.2f, RSI_buy: %.2f, RSI_sell: %.2f' %
        #       (self.data.datetime.datetime(0),
        #        self.atr.lines.signal[0],
        #        self.rsi.lines.signal[0],
        #        self.rsi.lines.signal_buy[0],
        #        self.rsi.lines.signal_sell[0])
        #       )

        # Check if an order is in Pending state, if yes, we cannot send a 2nd one
        if self.order:
            print('An order already in Pending state:')
            return

        # Check whether we have an open position already, if no, then we can enter a new position by entering a trade
        if self.position.size == 0:
        # if not self.position:
        #     if self.rsi.lines.signal_buy[0] > 0:
            if self.rsi.lines.signal[0] > 0:
                pstop = self.atr.lines.signal_stopbuy[0]
                pprof = self.dataclose[0] + self.rsi.params.target

                self.price_at_signal = self.dataclose[0]

                self.buy()
                # orders = self.buy(price=None,oargs=dict(exectype=bt.Order.Market,valid=datetime.timedelta(self.params.limdays)),
                #                   stopprice=pstop, stopargs=dict(exectype=bt.Order.Limit),
                #                   limitprice=pprof, limitargs=dict(exectype=bt.Order.Limit),)
                # order = self.buy(valid=datetime.timedelta(self.params.limdays))
                self.trades += 1

                # orderstop = self.sell(exectype=bt.Order.Limit,
                #                       price=pstop,
                #                       # oco=order,
                #                       valid=datetime.timedelta(self.params.limdays))
                # orderprof = self.sell(exectype=bt.Order.Limit,
                #                       price=pprof,
                #                       oco=orderstop,
                #                       valid=datetime.timedelta(self.params.limdays))
                #
                # # self.orefs = [order.ref, orderstop.ref, orderprof.ref]
                # self.orefs = [orderstop.ref, orderprof.ref]

                # self.log('Datetime: %s, Oref: %s, BUY at %.2f, stoploss: %.2f, takeprofit: %.2f' %
                #          (self.data.datetime.datetime(0),
                #           order.ref,
                #           self.dataclose[0],
                #           pstop,
                #           pprof)
                #          )

                self.log('BUY Signal, Close: %.2f, Stop: %.2f, ATR: %.2f, Signal: %.2f' %
                         (self.dataclose[0],
                          pstop,
                          self.atr.lines.signal[0],
                          self.rsi.lines.signal[0])
                         )

            # elif self.rsi.lines.signal_sell[0] > 0:
            elif self.rsi.lines.signal[0] > 0:
                pstop = self.atr.lines.signal_stopsell[0]
                # pprof = self.dataclose[0] + self.rsi.params.target
                self.price_at_signal = self.dataclose[0]

                self.sell()
                # order = self.sell(valid=datetime.timedelta(self.params.limdays))
                self.trades += 1

                # orderstop = self.buy(exectype=bt.Order.Limit,
                #                      price=pstop,
                #                      # oco=order,
                #                      valid=datetime.timedelta(self.params.limdays))
                # orderprof = self.buy(exectype=bt.Order.Limit,
                #                      price=pprof,
                #                      oco=orderstop,
                #                      valid=datetime.timedelta(self.params.limdays))

                # self.orefs = [order.ref, orderstop.ref, orderprof.ref]
                # self.orefs = [orderstop.ref, orderprof.ref]

                # self.log('Datetime: %s, Oref: %s, SELL at %.2f, stoploss: %.2f, takeprofit: %.2f' %
                #          (self.data.datetime.datetime(0),
                #           order.ref,
                #           self.dataclose[0],
                #           pstop,
                #           pprof)
                #          )

                self.log('SELL Signal, Close: %.2f, Stop: %.2f, ATR: %.2f, Signal: %.2f' %
                         (self.dataclose[0],
                          pstop,
                          self.atr.lines.signal[0],
                          self.rsi.lines.signal[0])
                         )

            else:
                self.log("Nothing, wait.")


class MainStrategy2(bt.Strategy):
    args = parse_args()

    params = (('plot_entry', True),
              ('plot_exit', True),
              ('limdays', 1),   #limit of days of alive orders
              )

    def log(self, txt, dt=None):
        """Logging function for this strategy"""
        dt = dt or self.datas[0].datetime.datetime(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):

        # To keep track of pending orders and buy price / commission.
        self.order = None

        # Keep a reference to the OHLC line in the data[0] dataseries
        self.dataopen = self.datas[0].open
        self.datahigh = self.datas[0].high
        self.datalow = self.datas[0].low
        self.dataclose = self.datas[0].close

        self.atr = ATRSignal()
        self.rsi = RSISignal()
        self.willr = WillRSignal()
        self.time_signal = TIMESignal()

        self.orefs = list()

    def notify_trade(self, trade):
        """Receives a trade whenever there has been a change in one"""
        if not trade.isclosed:
            return

        self.log('OPERATION PROFIT, REF: %s, PRICE: %.2f, GROSS %.2f' %
                 (trade.ref,
                  trade.price,
                  trade.pnl,
                  ))

    def notify_order(self, order):
        """Receives an order whenever there has been a change in one"""
        # print('{}: Order ref: {} / Type {} / Status {}'.format(
        #     self.data.datetime.date(0),
        #     order.ref,
        #     'Buy' * order.isbuy() or 'Sell',
        #     order.getstatusname()))

        # Check whether an order has enought Margin to call or was Rejected by the Broker
        if order.status in [order.Margin, order.Rejected]:
            self.log('REJECTED ORDER. Type: %s, REF: %s, PRICE: %.2f, SIZE: %.2f' %
                     (order.getstatusname(),
                      order.ref,
                      order.executed.price,
                      order.executed.size,
                      ))

        # Check whether an order is Submitted or Accepted by the Broker
        if order.status in [order.Submitted, order.Accepted]:
            # Order accepted by the broker. Do nothing.
            # self.log('ACCEPTED ORDER. STATUS: %s, Type: %s, REF: %s, PRICE: %.2f, SIZE: %.2f' %
            #          (order.getstatusname(),
            #           'Buy' * order.isbuy() or 'Sell',
            #           order.ref,
            #           order.executed.price,
            #           order.executed.size,
            #           ))
            return

        elif order.status in [order.Cancelled]:
            self.log('CANCEL ORDER. STATUS: %s, Type: %s, REF: %s, PRICE: %.2f, SIZE: %.2f' %
                     (order.getstatusname(),
                      'Buy' * order.isbuy() or 'Sell',
                      order.ref,
                      order.executed.price,
                      order.executed.size,
                      ))

        # Check if an order is completed
        elif order.status in [order.Completed]:
            self.log("COMPLETED ORDER. STATUS: %s, Type: %s, REF: %s, PRICE : %.3f, SIZE : %.2f" %
                     (order.getstatusname(),
                      'Buy' * order.isbuy() or 'Sell',
                      order.ref,
                      order.executed.price,
                      order.executed.size,
                      ))

        # if not order.alive():
        #     self.order = None  # indicate no order is pending
        if not order.alive() and order.ref in self.orefs:
            self.orefs.remove(order.ref)

    def next(self):
        """Simply log the closing price of the series from the reference"""

        print('Datetime: %s, Open: %.2f, High: %.2f, Low: %.2f, Close: %.2f' %
              (self.data.datetime.datetime(0),
               self.dataopen[0],
               self.datahigh[0],
               self.datalow[0],
               self.dataclose[0])
              )

        # Check if an order is in Pending state, if yes, we cannot send a 2nd one
        # if self.order:
        #     print('An order already in Pending state:')
        #     return
        if self.orefs:
            print('An order already in Pending state:')
            return  # pending orders do nothing

        # Check whether we have an open position already, if no, then we can enter a new position by entering a trade
        if not self.position:
            valid = datetime.timedelta(self.params.limdays)

            if self.time_signal.signal[0] == 0:
                print('Out of schedule time of operation')

            # elif self.rsi.lines.signal_buy[0] > 0:
            elif self.rsi.lines.signal[0] > 0:
                stop_loss = self.atr.lines.signal_stopbuy[0]
                take_profit = self.atr.lines.signal_profit_buy[0]
                # take_profit = self.dataclose[0] + self.rsi.params.target

                os = self.buy_bracket(price=None, valid=valid,
                                      stopprice=stop_loss, stopargs=dict(valid=valid),
                                      limitprice=take_profit, limitargs=dict(valid=valid),
                                      )
                self.orefs = [o.ref for o in os]

            # elif self.rsi.lines.signal_sell[0] > 0:
            elif self.rsi.lines.signal[0] < 0:
                stop_loss = self.atr.lines.signal_stopsell[0]
                take_profit = self.atr.lines.signal_profit_sell[0]
                # take_profit = self.dataclose[0] - self.rsi.params.target

                os = self.sell_bracket(price=None, valid=valid,
                                       stopprice=stop_loss, stopargs=dict(valid=valid),
                                       limitprice=take_profit, limitargs=dict(valid=valid),
                                       )
                self.orefs = [o.ref for o in os]

                self.log('Signal, Close: %.2f, Stop: %.2f, Profit: %.2f, ATR: %.2f, RSI Signal: %.2f' %
                         (self.dataclose[0],
                          stop_loss,
                          take_profit,
                          self.atr.lines.signal[0],
                          self.rsi.lines.signal[0])
                         )

            # else:
            #     self.log("Nothing, wait.")

        elif self.position:
            if self.time_signal.signal[0] == 0:
                print('Out of schedule time of operation, closing operation')
                self.close()


