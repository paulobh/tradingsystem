from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import argparse
import collections
import datetime
import numpy

# Import the backtrader platform
import backtrader as bt
import quantstats

from args import parse_args
import signals
from time import process_time


# Create a Stratey
class MainStrategy(bt.Strategy):
    params = (('plot_entry', True),
              ('plot_exit', True),
              ('limdays', 1),   #limit of days of alive orders
              )

    def log(self, txt, dt=None):
        """Logging function for this strategy"""
        dt = dt or self.datas[0].datetime.datetime(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self, **kwargs):
        # self.__dict__.update(kwargs)
        # allowed_keys = {'args', 'period_rsi', 'threshold_buy', 'threshold_sell'}
        # self.__dict__.update((k, v) for k, v in kwargs.items() if k in allowed_keys)

        # To keep track of pending orders and buy price / commission.
        self.order = None
        self.buyprice = None
        self.buycomm = None

        # Keep a reference to the OHLC line in the data[0] dataseries
        self.dataopen = self.datas[0].open
        self.datahigh = self.datas[0].high
        self.datalow = self.datas[0].low
        self.dataclose = self.datas[0].close

        # Add indicators signals
        self.atr = signals.ATRSignal()
        self.rsi = signals.RSISignal()
        self.willr = signals.WillRSignal()
        self.time_signal = signals.TIMESignal()

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

                os = self.buy_bracket(price=None, valid=valid,
                                      stopprice=stop_loss, stopargs=dict(valid=valid),
                                      limitprice=take_profit, limitargs=dict(valid=valid),
                                      )
                self.orefs = [o.ref for o in os]

            elif self.rsi.lines.signal[0] < 0:
                stop_loss = self.atr.lines.signal_stopsell[0]
                take_profit = self.atr.lines.signal_profit_sell[0]

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

        elif self.position:
            if self.time_signal.signal[0] == 0:
                print('Out of schedule time of operation, closing operation')
                self.close()


class OptStrategy(bt.Strategy):
    params = (
        # ('plot_entry', True),
        # ('plot_exit', True),
        ('limdays', 1),   #limit of days of alive orders
        # ('printlog', True),
        # ('signal', None),
    )

    def log(self, txt, dt=None, doprint=False):
        """Logging function for this strategy"""
        if self.params.printlog or doprint:
            dt = dt or self.datas[0].datetime.datetime(0)
            print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self, **kwargs):
        self.params_opt = kwargs
        self.params.__dict__.update(kwargs)
        self.__dict__.update(kwargs)
        # allowed_keys = {'args', 'period_rsi', 'threshold_buy', 'threshold_sell'}
        # self.__dict__.update((k, v) for k, v in kwargs.items() if k in allowed_keys)

        self.tstart = process_time()
        self.initial_value = self.broker.getvalue()

        # Activate the fund mode and set the default value at 100
        self.broker.set_fundmode(fundmode=True, fundstartval=100.00)
        self.cash_start = self.broker.get_cash()
        self.val_start = 100.0

        # To keep track of pending orders and buy price / commission.
        self.order = None
        self.buyprice = None
        self.buycomm = None

        # Keep a reference to the OHLC line in the data[0] dataseries
        self.dataopen = self.datas[0].open
        self.datahigh = self.datas[0].high
        self.datalow = self.datas[0].low
        self.dataclose = self.datas[0].close

        # Add indicators signals
        self.time_signal = signals.TIMESignal()
        self.atr = signals.ATRSignal()
        self.signal = getattr(signals, self.signal)(**kwargs)
        # self.rsi = RSISignal()
        # self.willr = WillRSignal()
        # self.sma = SMASignal(**kwargs)

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
            self.order = None

    def next(self):
        """Simply log the closing price of the series from the reference"""

        self.log('Datetime: %s, Open: %.2f, High: %.2f, Low: %.2f, Close: %.2f' %
        # print('Datetime: %s, Open: %.2f, High: %.2f, Low: %.2f, Close: %.2f' %
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
            # print('An order already in Pending state:')
            self.log('An order already in Pending state:')
            if self.time_signal.signal[0] == 0:
                self.log('Out of schedule time of operation, closing operation')
                # print('Out of schedule time of operation, closing operation')
                self.close()
                self.orefs = list()

            return  # pending orders do nothing

        # Check whether we have an open position already, if no, then we can enter a new position by entering a trade
        if not self.position:
            valid = datetime.timedelta(self.params.limdays)

            if self.time_signal.signal[0] == 0:
                # print('Out of schedule time of operation')
                return

            elif self.signal.lines.signal[0] > 0:
                stop_loss = self.atr.lines.signal_stopbuy[0]
                take_profit = self.atr.lines.signal_profit_buy[0]

                os = self.buy_bracket(price=None, valid=valid,
                                      stopprice=stop_loss, stopargs=dict(valid=valid),
                                      limitprice=take_profit, limitargs=dict(valid=valid),
                                      )
                self.orefs = [o.ref for o in os]

            elif self.signal.lines.signal[0] < 0:
                stop_loss = self.atr.lines.signal_stopsell[0]
                take_profit = self.atr.lines.signal_profit_sell[0]

                os = self.sell_bracket(price=None, valid=valid,
                                       stopprice=stop_loss, stopargs=dict(valid=valid),
                                       limitprice=take_profit, limitargs=dict(valid=valid),
                                       )
                self.orefs = [o.ref for o in os]

                signal_name = [line for line in self.signal.lines.getlinealiases() if line != "signal"][0]

                self.log('Signal, Close: %.2f, Stop: %.2f, Profit: %.2f, ATR: %.2f, Signal: %.2f, Indicator: %s, Value: %.2f' %
                         (self.dataclose[0],
                          stop_loss,
                          take_profit,
                          self.atr.lines.signal[0],
                          self.signal.lines.signal[0],
                          signal_name,
                          getattr(self.signal.lines, signal_name)[0])
                         )

    def stop(self):
        self.tend = process_time()
        time_spent = self.tend - self.tstart
        # print('Time used:', str(time_spent))

        self.final_value = self.broker.getvalue()
        balance = self.final_value - self.initial_value

        self.roi = (self.broker.get_value() / self.cash_start) - 1.0
        self.froi = self.broker.get_fundvalue() - self.val_start

        params_pop = ['plot_entry', 'plot_exit', 'limdays', 'printlog']
        [self.params_opt.pop(param) for param in params_pop if param in self.params_opt]
        self.log(
                 f'Parameters used: {self.params_opt}| '
                 f'ROI: {100.0 * self.roi}| '
                 f'Fund Value {self.froi}| '                 
                 f'Ending Value: {balance}',

                 doprint=True)




class TestStrategy(bt.Strategy):
    params = (
        ('maperiod', 15),
        ('printlog', False),
    )

    def log(self, txt, dt=None, doprint=False):
        ''' Logging function fot this strategy'''
        if self.params.printlog or doprint:
            dt = dt or self.datas[0].datetime.date(0)
            print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):

        # To keep track of pending orders and buy price/commission
        self.order = None
        self.buyprice = None
        self.buycomm = None

        # Keep a reference to the OHLC line in the data[0] dataseries
        self.dataopen = self.datas[0].open
        self.datahigh = self.datas[0].high
        self.datalow = self.datas[0].low
        self.dataclose = self.datas[0].close

        # Add a MovingAverageSimple indicator
        self.sma = bt.indicators.SimpleMovingAverage(
            self.datas[0], period=self.params.maperiod)
        # self.sma = SMASignal()

        self.orefs = list()

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    'BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                    (order.executed.price,
                     order.executed.value,
                     order.executed.comm))

                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            else:  # Sell
                self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                         (order.executed.price,
                          order.executed.value,
                          order.executed.comm))

            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        # Write down: no pending order
        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' %
                 (trade.pnl, trade.pnlcomm))

    def next(self):
        # Simply log the closing price of the series from the reference
        self.log('Close, %.2f' % self.dataclose[0])

        # Check if an order is pending ... if yes, we cannot send a 2nd one
        if self.order:
            return
        # if self.orefs:
        #     print('An order already in Pending state:')
        #     return  # pending orders do nothing

        # Check if we are in the market
        if not self.position:

            # Not yet ... we MIGHT BUY if ...
            # if self.sma.lines.signal[0] > 0:
            if self.dataclose[0] > self.sma[0]:

                # BUY, BUY, BUY!!! (with all possible default parameters)
                self.log('BUY CREATE, %.2f' % self.dataclose[0])

                # Keep track of the created order to avoid a 2nd order
                self.order = self.buy()

        else:
            if self.dataclose[0] < self.sma[0]:
            # elif self.dataclose[0] < self.sma[0]:
            # elif self.sma.lines.signal[0] < 0:
                # SELL, SELL, SELL!!! (with all possible default parameters)
                self.log('SELL CREATE, %.2f' % self.dataclose[0])

                # Keep track of the created order to avoid a 2nd order
                self.order = self.sell()

    def stop(self):
        self.log('(MA Period %2d) Ending Value %.2f' %
                 (self.params.maperiod, self.broker.getvalue()), doprint=True)
