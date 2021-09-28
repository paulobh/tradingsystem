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

# from src.strategies import MainStrategy
# from strategies import TestStrategy
from src import strategies


def runstrat_main(settings, **kwargs):
    # clock the start of the process
    tstart = process_time()

    args = parse_args(kwargs)
    # signal = list(kwargs["signal"].keys())[0]

    # Create a cerebro entity
    cerebro = bt.Cerebro(stdstats=False,        # default kwarg: stdstats=True
                         # maxcpus=args.maxcpus,
                         # runonce=not args.no_runonce,
                         # exactbars=args.exactbars,
                         # optdatas=not args.no_optdatas,
                         # optreturn=not args.no_optreturn
                         )


    # Add a strategy
    cerebro.addstrategy(strategies.MainStrategy, **settings, **kwargs)

    # Get a data source path
    datapath = args.data

    # Pass it to the backtrader datafeed and add it to the cerebro
    data = bt.feeds.PandasData(dataname=pandasdatafeed(datapath, args=args),
                               fromdate=args.fromdate,  # fromdate=args.fromdate,
                               todate=args.todate)  # todate=args.todate)
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

    # Set Analyzer
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='tradeanalyzer')  # muito completo
    # cerebro.addanalyzer(bt.analyzers.TimeDrawDown, _name='timedrawdown')
    cerebro.addanalyzer(bt.analyzers.VWR, _name='vwr')  # VariabilityWeightedReturn
    cerebro.addanalyzer(bt.analyzers.SQN, _name='sqn')  # SystemQualityNumber.

    # Writer
    # cerebro.addwriter(bt.WriterFile, csv=True, out='./logs/log.csv')
    # cerebro.addwriter(bt.WriterFile, csv=args.writercsv, out='./logs/log.csv')

    # Print out the starting conditions
    # print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

    # Run over everything
    results = cerebro.run()

    # # Extract/save analyzers
    # analyzers_log(settings, results)

    # clock the end of the process
    tend = process_time()

    # print out the result
    print('Time used:', str(tend - tstart))

    # # Plot the result
    # if args.plot:
    #     pkwargs = dict(style='bar')
    #     # pkwargs = dict(style='ohlc')
    #     if args.plot is not True:  # evals to True but is not True
    #         npkwargs = eval('dict(' + args.plot + ')')  # args were passed
    #         pkwargs.update(npkwargs)
    #     cerebro.plot(**pkwargs)
    # # cerebro.plot(style='bar', bardist=0)

    # Print out the final result
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())


def main(settings, **kwargs):
    # params_settings = settings["opt_params"]
    filename = settings["opt_analyzer"]["path_opt_parms"]

    # data = json.load(open(filename, "r"))
    params = {}
    # params.update(data)
    params.update({"signal": {"ElderForceIndexSignal": {}}})

    # run strategy
    runstrat_main(settings, **params)

    return None


if __name__ == '__main__':
    settings = json.load(open("./src/settings.json"))

    # clock the start of the process
    tstart = process_time()

    # main script
    main(settings)

    # clock the end of the process
    tend = process_time()

    # print out the result
    print('Total Time used:', str(tend - tstart))
