from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import datetime  # For datetime objects
import os.path  # To manage paths
import sys  # To find out the script name (in argv[0])
import argparse

import backtrader as bt  # Import the backtrader platform

from datafeed import pandasdatafeed
from strategies import TestStrategy
from strategies import MainStrategy
from strategies import MainStrategy2
from args import parse_args


def runstrat(args=None):
    args = parse_args(args)

    # Create a cerebro entity
    cerebro = bt.Cerebro()
    # cerebro = bt.Cerebro(stdstats=False)
    # cerebro = bt.Cerebro(tradehistory=True)

    # Add a strategy
    # cerebro.addstrategy(TestStrategy)
    # cerebro.addstrategy(MainStrategy)
    cerebro.addstrategy(MainStrategy2)

    # Get a pandas dataframe
    datapath = args.data

    # Pass it to the backtrader datafeed and add it to the cerebro
    data = bt.feeds.PandasData(dataname=pandasdatafeed(datapath),
                               fromdate=args.fromdate,
                               todate=args.todate)

    cerebro.adddata(data)

    # Set our desired cash start
    # cerebro.broker.setcash(100000.0)
    cerebro.broker.setcash(args.cash)

    # Add a FixedSize sizer according to the stake
    cerebro.addsizer(bt.sizers.FixedSize, stake=1)

    # Print out the starting conditions
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

    # Run over everything
    cerebro.run()

    # Plot the result
    # cerebro.plot(style='bar')
    if args.plot:
        pkwargs = dict(style='bar')
        if args.plot is not True:  # evals to True but is not True
            npkwargs = eval('dict(' + args.plot + ')')  # args were passed
            pkwargs.update(npkwargs)
        cerebro.plot(**pkwargs)


    # Print out the final result
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())


if __name__ == '__main__':
    runstrat()
