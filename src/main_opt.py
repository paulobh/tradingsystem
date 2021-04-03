from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import datetime  # For datetime objects
import os.path  # To manage paths
import sys  # To find out the script name (in argv[0])
import argparse
import json
import datetime
from time import process_time

import backtrader as bt  # Import the backtrader platform
# from backtrader.utils.py3 import range
from datafeed import pandasdatafeed
# from strategies import TestStrategy
# from strategies import MainStrategy
# from strategies import TestStrategy
from args import parse_args
import collections
import strategies





def runstrat(**kwargs):
    # clock the start of the process
    tstart = process_time()

    args = parse_args()
    signal = list(kwargs.keys())[0]

    # Create a cerebro entity
    # cerebro = bt.Cerebro(stdstats=False)
    cerebro = bt.Cerebro(stdstats=False,
                         maxcpus=args.maxcpus,
                         runonce=not args.no_runonce,
                         exactbars=args.exactbars,
                         optdatas=not args.no_optdatas,
                         optreturn=not args.no_optreturn)

    # Add a strategy
    # cerebro.addstrategy(strategies.OptStrategy)
    cerebro.optstrategy(
        # strategies.TestStrategy,
        # maperiod=range(15, 25)
        # strategies.OptStrategy,
        # period_sma=range(*params["SMASignal"]["period_sma"]),
        # signal="SMASignal",
        # period_sma=range(*kwargs["period_sma"]),
        # period_sma=range(*kwargs[signal]["period_sma"]),
        # period_sma=[20, 21, 22, 23, 24, 25],
        # **{'period_sma':[20, 21, 22, 23, 24, 25]},
        strategies.OptStrategy,
        **kwargs.get(signal),
        signal=signal,
        printlog=False
        )

    datapath = args.data
    data = bt.feeds.PandasData(dataname=pandasdatafeed(datapath, args=args),
                               fromdate=args.fromdate,
                               todate=args.todate
                               )
    cerebro.adddata(data)

    # Set our desired cash start
    cerebro.broker.setcash(args.cash)  # cerebro.broker.setcash(100000.0)

    # Print out the starting conditions
    # print('Starting Portfolio Value: %.2f' % initial_value)
    # initial_value = cerebro.broker.getvalue()

    # Add a FixedSize sizer according to the stake
    cerebro.addsizer(bt.sizers.FixedSize, stake=1)

    # Set the commission
    cerebro.broker.setcommission(commission=0.0)

    # Set Observer
    cerebro.addobserver(bt.observers.Broker)
    cerebro.addobserver(bt.observers.Trades)
    cerebro.addobserver(bt.observers.BuySell, barplot=True, bardist=0.0025)
    cerebro.addobserver(bt.observers.DrawDown)

    # Analyzer
    # cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='mysharpe')
    cerebro.addanalyzer(bt.analyzers.PyFolio, _name='pyfolio')

    # Run over everything
    cerebro.run()

    # strat = results[0]
    # pyfoliozer = strat.analyzers.getbyname('pyfolio')
    # returns, positions, transactions, gross_lev = pyfoliozer.get_pf_items()


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
    # final_value = cerebro.broker.getvalue()
    # print('Final Portfolio Value: %.2f' % final_value)

    # print('==================================================')
    # for stratrun in results:
    #     print('**************************************************')
    #     for strat in stratrun:
    #         print('--------------------------------------------------')
    #         print(strat.p._getkwargs())
    # print('==================================================')

    # clock the end of the process
    # tend = process_time()

    # print out the result
    # print('Time used:', str(tend - tstart))
    print('Time used:', str(process_time() - tstart))
    # print('Final balance:', str(final_value - initial_value))


def main(**kwargs):
    params = json.load(open("./src/opt_params.json"))

    # signals = list(list(params.keys())[-1])
    signals = ["SMASignal"]
    # signals = ["SMASignal", "RSISignal"]
    params_signal = {key: params.get(key) for key in params if key in signals}
    params_signal = {signal: {key: range(*params.get(signal).get(key)) for key in params.get(signal)} for signal in params_signal}
    # params_signal = [params.get(key) for key in signals]
    # params_signal = params.get("SMASignal")

    runstrat(**params_signal)
    return None

if __name__ == '__main__':
    # runstrat()
    main()
