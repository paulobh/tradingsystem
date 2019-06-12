from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import datetime  # For datetime objects
import os.path  # To manage paths
import sys  # To find out the script name (in argv[0])
import argparse

import backtrader as bt  # Import the backtrader platform

from datafeed import pandasdatafeed
from strategies import TestStrategy
from args import parse_args


def runstrat(args=None):
    args = parse_args(args)

    # Create a cerebro entity
    cerebro = bt.Cerebro()
    # cerebro = bt.Cerebro(stdstats=False)

    # Add a strategy
    cerebro.addstrategy(TestStrategy)

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

    # Print out the starting conditions
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

    # Run over everything
    cerebro.run()

    # Plot the result
    cerebro.plot(style='bar')

    # Print out the final result
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())


if __name__ == '__main__':
    runstrat()
