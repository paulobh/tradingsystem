from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import glob
import json

import pandas

import strategies
import backtrader as bt  # Import the backtrader platform
import datetime  # For datetime objects
# import os.path  # To manage paths
# import sys  # To find out the script name (in argv[0])
# import argparse

from args import parse_args
from time import process_time
from datafeed import pandasdatafeed
from backtrader.utils.py3 import range
# from strategies import TestStrategy
# from strategies import MainStrategy
# from strategies import TestStrategy
# import collections
# import quantstats

TFRAMES = dict(
    minutes=bt.TimeFrame.Minutes,
    days=bt.TimeFrame.Days,
    weeks=bt.TimeFrame.Weeks,
    months=bt.TimeFrame.Months,
    years=bt.TimeFrame.Years)


def runstrat(**kwargs):
    # clock the start of the process
    tstart = process_time()

    args = parse_args()
    signal = list(kwargs.keys())[0]

    # Create a cerebro entity
    cerebro = bt.Cerebro(stdstats=False,
                         maxcpus=args.maxcpus,
                         runonce=not args.no_runonce,
                         exactbars=args.exactbars,
                         optdatas=not args.no_optdatas,
                         optreturn=not args.no_optreturn
                         )

    # Add a strategy
    cerebro.optstrategy(
        strategies.OptStrategy,
        **kwargs.get(signal),
        signal=signal,
        # printlog=False
        )

    datapath = args.data
    data = bt.feeds.PandasData(dataname=pandasdatafeed(datapath, args=args),
                               fromdate=args.fromdate,
                               todate=args.todate)
    cerebro.adddata(data)

    # Set our desired cash start
    cerebro.broker.setcash(args.cash)  # cerebro.broker.setcash(100000.0)

    # Add a FixedSize sizer according to the stake
    cerebro.addsizer(bt.sizers.FixedSize, stake=1)

    # Set the commission
    cerebro.broker.setcommission(commission=0.0)

    # Analyzer
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='tradeanalyzer')  # muito completo
    cerebro.addanalyzer(bt.analyzers.TimeDrawDown, _name='timedrawdown')
    cerebro.addanalyzer(bt.analyzers.VWR, _name='vwr')  # VariabilityWeightedReturn
    cerebro.addanalyzer(bt.analyzers.SQN, _name='sqn')  # SystemQualityNumber.

    # Writer
    # cerebro.addwriter(bt.WriterFile, csv=True, out='./logs/log.csv')
    # cerebro.addwriter(bt.WriterFile, csv=args.writercsv, out='./logs/log.csv')

    # Run over everything
    results = cerebro.run()

    # Extract/save analyzers
    analyzers_log(results)

    # clock the end of the process
    tend = process_time()

    # print out the result
    print('Time used:', str(tend - tstart))


def analyzers_log(results):
    analyzers_dict = {}
    params_pop = ['plot_entry', 'plot_exit', 'limdays', 'printlog']
    for stratrun in results:
        for strat in stratrun:
            params = strat.params.__dict__
            [params.pop(param) for param in params_pop if param in params]
            analysis_value = {analyzer.__class__.__name__: analyzer.get_analysis() for analyzer in strat.analyzers}
            analysis_key = json.dumps(params)
            analyzers_dict.update({analysis_key: analysis_value})
    filepath = f"./data/analyzers_opt/analyzer_{params['signal']}.json"
    json.dump(analyzers_dict, open(filepath, "w"), sort_keys=True, indent=4)
    return None


def analyzers_read(filepath="./data/analyzers_opt/analyzer_*.json"):
    analyzers_keys = {
        "SQN": ["sqn"],
        "VWR": ["vwr"],
        "TimeDrawDown": ["maxdrawdown", "maxdrawdownperiod"]
    }
    # allowed_keys = {'args', 'period_rsi', 'threshold_buy', 'threshold_sell'}
    # self.__dict__.update((k, v) for k, v in kwargs.items() if k in allowed_keys)

    files = glob.glob(filepath)
    for file in files:
        analyzers = json.load(open(file, 'r'))
        analyzers = {tuple(json.loads(key).items()): value for key, value in analyzers.items()}
        analyzers_df = pandas.DataFrame()
        df = pandas.DataFrame(analyzers).T
        for key, values in analyzers_keys.items():
            df_sample = df[key].apply(pandas.Series).loc[:, values]
            analyzers_df = pandas.concat([analyzers_df, df_sample], axis=1)
        file = file.replace(".json", ".csv")
        analyzers_df.to_csv(file, sep=";")
    return None



def main(**kwargs):
    params = json.load(open("./src/opt_params.json"))

    # params_signal = [params.get(key) for key in signals]
    # params_signal = params.get("SMASignal")
    # signals = ["SMASignal"]
    signals = ["RSISignal"]
    # signals = ["SMASignal", "RSISignal"]

    for signal in signals:
        # Filter Signal to be used.
        params_signal = {key: params.get(key) for key in params if key in signal}

        # Fill range values.
        params_signal = {signal: {key: range(*params.get(signal).get(key))
                                  for key in params.get(signal)}
                         for signal in params_signal}

        # run optimization strategy
        runstrat(**params_signal)

    # analyzers_read()
    return None


if __name__ == '__main__':
    # runstrat()
    main()
