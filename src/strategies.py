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

    lines = (('signal'),
             ('signal_atr'),
             )
    params = (('period_atr', 20),
              ('atrdist', 1.0),  # ATR distance for stop price
              )
    plotinfo = dict(subplot=False)

    def __init__(self):
        self.atr = bt.indicators.AverageTrueRange(period=self.params.period_atr) * self.params.atrdist // 1
        self.lines.signal = self.atr
        self.lines.signal_atr = self.data - self.atr


class RSISignal(bt.Indicator):
    args = parse_args()

    lines = (('signal'),
             ('signal_buy'),
             ('signal_sell'),
             )
    params = (('period_rsi', 20),
              ('threshold_buy', 30),
              ('threshold_sell', 70),
              ('target', 400),
              )
    plotinfo = dict(subplot=False)

    def __init__(self):
        self.rsi = bt.indicators.RelativeStrengthIndex(period=self.params.period_rsi)
        self.threshold_buy = self.params.threshold_buy
        self.threshold_sell = self.params.threshold_sell

        self.lines.signal = self.rsi
        self.lines.signal_buy = self.threshold_buy - self.rsi
        self.lines.signal_sell = self.rsi - self.threshold_sell

        # plot indicators
        # bt.LinePlotterIndicator(self.threshold_buy*1, name='upband', subplot=False)
        # bt.LinePlotterIndicator(self.threshold_sell*1, name='downband', subplot=False)

        # to show date/time progress
        # self.trace = 0


# Create a Stratey
class TestStrategy(bt.Strategy):

    def log(self, txt, dt=None):
        ''' Logging function for this strategy'''
        # dt = dt or self.datas[0].datetime.date(0)
        dt = dt or self.datas[0].datetime.datetime(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        # Keep a reference to the "close" line in the data[0] dataseries
        self.dataclose = self.datas[0].close
        self.rsi = RSISignal()

    def next(self):
        # Simply log the closing price of the series from the reference
        self.log('Close, %.2f' % self.dataclose[0])
        # self.log('ATR, %.2f' % self.atr.signal[0])
        # self.log('ATR_sig, %.2f' % self.atr.signal_atr[0])
        self.log('RSI, %.2f' % self.rsi.signal_buy[0])


class MainStrategy(bt.Strategy):
    args = parse_args()

    params = (('plot_entry', True),
              ('plot_exit', True),
              ('use_target_size', False),
              ('use_target_value', False),
              ('use_target_percent', False),
              ('trailamount', 0.0),
              ('trailpercent', 0.0),
              )

    def log(self, txt, dt=None):
        """Logging function for this strategy"""
        # dt = dt or self.datas[0].datetime.date(0)
        dt = dt or self.datas[0].datetime.datetime(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):

        # To keep track of pending orders and buy price / commission.
        self.order = None
        self.orderprice = None
        self.commission = None
        self.orderstop = None
        self.pdist = None

        self.atr = ATRSignal()
        self.rsi = RSISignal()

        # Keep a reference to the OHLC line in the data[0] dataseries
        self.dataopen = self.datas[0].open
        self.datahigh = self.datas[0].high
        self.datalow = self.datas[0].low
        self.dataclose = self.datas[0].close

    def notify_order(self, order):
        """Receives an order whenever there has been a change in one"""

        # Check whether an order is Submitted or Accepted by the Broker
        if order.status in [order.Submitted, order.Accepted]:
            return

        # Check if an order is completed
        if order.status in [order.Completed]:

            if order.isbuy():
                # print('Buy Executed Price: %.2f, Cost : %.2f, Commission : %.2f' %
                print('Buy Executed Price: %.2f, Cost : %.2f, Stop : %.2f' %
                      (order.executed.price,
                       order.executed.value,
                       self.pstop
                       ))
                self.orderprice = order.executed.price
                self.orderstop = self.pstop

            elif order.issell():
                # print('Sell Executed Price: %.2f, Cost : %.2f, Commission : %.2f' %
                print('Sell Executed Price: %.2f, Cost : %.2f, Stop : %.2f' %
                      (order.executed.price,
                       order.executed.value,
                       self.pstop
                       ))
                self.orderprice = order.executed.price
                self.orderstop = self.pstop

            # self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
          print('Order Canceled/Margin/Rejected')

        self.order = None
        # if not order.alive():
        #     self.order = None  # indicate no order is pending

    def notify_trade(self, trade):
        """Receives a trade whenever there has been a change in one"""

        if not trade.isclosed:
            return

        print('OPERATION PROFIT, GROSS %.2f, NET %.2f' %
             (trade.pnl, trade.pnlcomm))

    def next(self):
        """Simply log the closing price of the series from the reference"""
        # print('Date, %s, Close, %.2f' % (self.data.datetime.date(0), self.dataclose[0]))
        # print('Datetime, %s, Close, %.2f' % (self.data.datetime.datetime(0), self.dataclose[0]))
        print('Datetime: %s, Open: %.2f, High: %.2f, Low: %.2f, Close: %.2f' %
              (self.data.datetime.datetime(0),
               self.dataopen[0],
               self.datahigh[0],
               self.datalow[0],
               self.dataclose[0])
              )
        # self.log('Close, %.2f' % self.dataclose[0])
        # self.log('ATR, %.2f' % self.atr.signal[0])
        # self.log('ATR_sig, %.2f' % self.atr.signal_atr[0])

        # Check if an order is in Pending state, if yes, we cannot send a 2nd one
        if self.order:
            print('An order already in Pending state')
            return

        # Check whether we have an open position already, if no, then we can enter a new position by entering a trade
        if not self.position:

            if self.rsi[0] != 0:

                if self.rsi[0] > 0:
                    self.order = self.buy()
                    self.pdist = self.atr[0]
                    self.pstop = self.data.close[0] - self.pdist
                    self.log('BUY Signal, Close: %.2f, Stop: %.2f, ATR: %.2f' %
                             (self.dataclose[0],
                              self.pstop,
                              self.pdist)
                             )

                elif self.rsi[0] < 0:
                    self.order = self.sell()
                    self.pdist = self.atr[0]
                    self.pstop = self.data.close[0] + self.pdist
                    # self.log('SELL Signal, %.2f' % (self.dataclose[0]))
                    self.log('SELL Signal, Close: %.2f, Stop: %.2f, ATR: %.2f' %
                             (self.dataclose[0],
                              self.pstop,
                              self.pdist)
                             )

        # if there is an existing position already, then we have to close it if:
        elif self.position:

            pclose = self.data.close[0]
            pstop = self.pstop

            # print(self.position.size())
            if pclose < pstop:
                self.close()  # stop met - get out
            else:
                self.pdist = self.atr[0]
                # Update only if greater than
                self.pstop = max(pstop, pclose - self.pdist)


