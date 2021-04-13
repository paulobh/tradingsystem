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
import quantstats



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
                         optreturn=not args.no_optreturn
                         )

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
        # **kwargs,
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
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='tradeanalyzer')  # muito completo, ate de +
    cerebro.addanalyzer(bt.analyzers.PeriodStats, _name='periodstats')
    cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')

    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
    cerebro.addanalyzer(bt.analyzers.TimeDrawDown, _name='timedrawdown')

    cerebro.addanalyzer(bt.analyzers.SQN, _name='sqn')  #   SystemQualityNumber.
    cerebro.addanalyzer(bt.analyzers.VWR, _name='vwr')  #   VariabilityWeightedReturn

    # cerebro.addanalyzer(bt.analyzers.Calmar, _name='calmar')    # precisa configurar melhor
    # cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe_ratio')     # precisa configurar melhor
    # cerebro.addanalyzer(bt.analyzers.SharpeRatio_A, _name='sharpe_ratio_a')     # precisa configurar melhor
    # cerebro.addanalyzer(bt.analyzers.PositionsValue, _name='positionsvalue')  # mostra valores diarios acumulados
    # cerebro.addanalyzer(bt.analyzers.LogReturnsRolling, _name='logreturnsrolling')  # mostra valores diarios acumulados
    # cerebro.addanalyzer(bt.analyzers.TimeReturn, _name='timereturn') # mostra valores diarios acumulados
    # AnnualReturn
    # GrossLeverage
    # PyFolio
    # Transactions

    # Writer
    # cerebro.addwriter(bt.WriterFile, csv=True, out='./logs/log.csv')
    # cerebro.addwriter(bt.WriterFile, csv=args.writercsv, out='./logs/log.csv')

    # Run over everything
    results = cerebro.run()

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

    analyzers_log(results)
    # print('==================================================')
    # for stratrun in results:
    #     for strat in stratrun:
    #         print(strat.p._getkwargs())
    #
    #         returns, positions, transactions, gross_lev = strat.analyzers.pyfolio.get_pf_items()
            # returns.index = returns.index.tz_convert(None)
            # pyfolio.create_full_tear_sheet(
            #     returns,
            #     positions=positions,
            #     transactions=transactions,
            #     gross_lev=gross_lev,
            #     # live_start_date='2005-05-01',  # This date is sample specific
            #     round_trips=True)
    #
    # print('==================================================')
    # quantstats.reports.html(results, output='./logs/stats.html', title='BTC Sentiment')



    # clock the end of the process
    # tend = process_time()

    # print out the result
    # print('Time used:', str(tend - tstart))
    print('Time used:', str(process_time() - tstart))
    # print('Final balance:', str(final_value - initial_value))

def analyzers_log(results):

    for stratrun in results:
        for strat in stratrun:
            params_pop = ['plot_entry', 'plot_exit', 'limdays', 'printlog']
            params = strat.params.__dict__
            [params.pop(param) for param in params_pop if param in params]
            print(params)
            # print(self.params._getkwargs())
            for analyzer in strat.analyzers:
                a = analyzer.get_analysis()
                print(analyzer.__class__.__name__, dict(a))

    return None






def main(**kwargs):
    params = json.load(open("./src/opt_params.json"))

    # signals = list(list(params.keys())[-1])
    # signals = ["SMASignal"]
    # signals = ["SMASignal", "RSISignal"]
    # params_signal = [params.get(key) for key in signals]
    # params_signal = params.get("SMASignal")
    # params_signal = {key: params.get(key) for key in params if key in signals}
    # params_signal = {signal: {key: range(*params.get(signal).get(key)) for key in params.get(signal)} for signal in
    #                  params_signal}
    signals = ["SMASignal"]
    # signals = ["RSISignal"]
    # Filter Signal to be used.
    params_signal = {key: params.get(key) for key in params if key in signals}
    # Fill range values.
    params_signal = {signal: {key: range(*params.get(signal).get(key))
                              for key in params.get(signal)}
                     for signal in params_signal}
    runstrat(**params_signal)
    return None


if __name__ == '__main__':
    # runstrat()
    main()
