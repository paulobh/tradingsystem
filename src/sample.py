from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import datetime  # For datetime objects
import os.path  # To manage paths
import sys  # To find out the script name (in argv[0])

# Import the backtrader platform
import backtrader as bt

from datafeed import pandasdatafeed
from strategies import TestStrategy


def runstrat(pargs=None):
    # Create a cerebro entity
    cerebro = bt.Cerebro()
    # cerebro = bt.Cerebro(stdstats=False)

    # Add a strategy
    cerebro.addstrategy(TestStrategy)

    # Get a pandas dataframe
    datapath = '../resources/WIN$N_15M.csv'
    dataframe = pandasdatafeed(datapath)

    # Pass it to the backtrader datafeed and add it to the cerebro
    data = bt.feeds.PandasData(dataname=dataframe)

    cerebro.adddata(data)

    # Set our desired cash start
    cerebro.broker.setcash(100000.0)

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