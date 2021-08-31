from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import backtrader as bt  # Import the backtrader platform
# import datetime  # For datetime objects
# import os.path  # To manage paths
# import sys  # To find out the script name (in argv[0])
# import argparse
import pandas
import glob
import json
import datetime  # For datetime objects

from src.datafeed import pandasdatafeed
from time import process_time
from src.args import parse_args
from backtrader.utils.py3 import range

from src.strategies import MainStrategy
# from strategies import TestStrategy
from src import strategies
from src import main_opt


def runstrat_main(args=None, **kwargs):
    # clock the start of the process
    tstart = process_time()

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
    print('Time used:', str(tend - tstart))

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


def analyzers_opt_params(settings, **kwargs):
    filename = settings["opt_analyzer"]["path_opt_parms"]
    return


def main(settings, **kwargs):
    params_settings = settings["opt_params"]
    filename = settings["opt_analyzer"]["path_opt_parms"]

    dates = main_opt.daterange_opt(settings)
    params = {}

    for idx, date in dates.items():
        fromdate, todate = date["test"]
        params.update({"fromdate": fromdate, "todate": todate})

        # run optimization strategy
        runstrat_main(settings, **params)
        # read analyzers and save output
        main_opt.analyzers_read(settings, **params)
    return None


if __name__ == '__main__':
    settings = json.load(open("./src/settings.json"))

    # generate optimization params
    main_opt.main_opt(settings)

    # run strategy with opt params
    # runstrat_main()
