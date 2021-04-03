from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import datetime  # For datetime objects
import os.path  # To manage paths
import sys  # To find out the script name (in argv[0])
import argparse
import json
from time import process_time

import backtrader as bt  # Import the backtrader platform

from datafeed import pandasdatafeed
# from strategies import TestStrategy
# from strategies import MainStrategy
from strategies import MainStrategy
from args import parse_args


def runstrat(args=None):
    args = parse_args(args)

    # Create a cerebro entity
    cerebro = bt.Cerebro(stdstats=False)  # default kwarg: stdstats=True

    # Add a strategy
    cerebro.addstrategy(MainStrategy)

    # Get a pandas dataframe
    # modpath = os.path.dirname(os.path.abspath(sys.argv[0]))
    # datapath = os.path.join(modpath, '../WIN$N_5M_2015.05.22_2021.01.22_.csv')
    datapath = args.data

    # Pass it to the backtrader datafeed and add it to the cerebro
    data = bt.feeds.PandasData(dataname=pandasdatafeed(datapath, args=args),
                               fromdate=args.fromdate,
                               todate=args.todate
                               )
    cerebro.adddata(data)

    # Set our desired cash start
    cerebro.broker.setcash(args.cash)   # cerebro.broker.setcash(100000.0)

    # Add a FixedSize sizer according to the stake
    cerebro.addsizer(bt.sizers.FixedSize, stake=1)

    # Set the commission
    cerebro.broker.setcommission(commission=0.0)

    # Set Observer
    cerebro.addobserver(bt.observers.Broker)
    cerebro.addobserver(bt.observers.Trades)
    cerebro.addobserver(bt.observers.BuySell, barplot=True, bardist=0.0025)
    cerebro.addobserver(bt.observers.DrawDown)

    # Print out the starting conditions
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

    # clock the start of the process
    tstart = process_time()

    # Run over everything
    cerebro.run()

    # clock the end of the process
    tend = process_time()

    # Plot the result
    if args.plot:
        pkwargs = dict(style='bar')
        # pkwargs = dict(style='ohlc')
        if args.plot is not True:  # evals to True but is not True
            npkwargs = eval('dict(' + args.plot + ')')  # args were passed
            pkwargs.update(npkwargs)
        cerebro.plot(**pkwargs)
    # cerebro.plot(style='bar', bardist=0)

    # Print out the final result
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())


if __name__ == '__main__':
    runstrat()
