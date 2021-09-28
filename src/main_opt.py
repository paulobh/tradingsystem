from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import glob
import os
import json
import pandas
import numpy as np
from multiprocessing import Process

import pandas as pd

from src import strategies
# import strategies
import backtrader as bt  # Import the backtrader platform
import datetime  # For datetime objects
# import os.path  # To manage paths
# import sys  # To find out the script name (in argv[0])
# import argparse

from src.args import parse_args
from time import process_time
from src.datafeed import pandasdatafeed
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


class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return super(NpEncoder, self).default(obj)


def runstrat_opt(settings, **kwargs):
    # clock the start of the process
    tstart = process_time()

    args = parse_args(kwargs)
    signal = list(kwargs["signal"].keys())[0]

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
        **kwargs["signal"].get(signal),
        signal=signal,
        printlog=False
        )

    # Get a data source path
    datapath = args.data

    # Pass it to the backtrader datafeed and add it to the cerebro
    data = bt.feeds.PandasData(dataname=pandasdatafeed(datapath, args=args),
                               fromdate=args.train["fromdate"],      # fromdate=args.fromdate,
                               todate=args.train["todate"])          # todate=args.todate)
    cerebro.adddata(data)

    # Set our desired cash start
    cerebro.broker.setcash(args.cash)  # cerebro.broker.setcash(100000.0)

    # Add a FixedSize sizer according to the stake
    cerebro.addsizer(bt.sizers.FixedSize, stake=1)

    # Set the commission
    cerebro.broker.setcommission(commission=0.0)

    # Analyzer
    # cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='tradeanalyzer')  # muito completo
    # cerebro.addanalyzer(bt.analyzers.TimeDrawDown, _name='timedrawdown')
    cerebro.addanalyzer(bt.analyzers.VWR, _name='vwr')  # VariabilityWeightedReturn
    cerebro.addanalyzer(bt.analyzers.SQN, _name='sqn')  # SystemQualityNumber.

    # Writer
    # cerebro.addwriter(bt.WriterFile, csv=True, out='./logs/log.csv')
    # cerebro.addwriter(bt.WriterFile, csv=args.writercsv, out='./logs/log.csv')

    # Run over everything
    results = cerebro.run()

    # Extract/save analyzers
    analyzers_log(settings, results)

    # clock the end of the process
    tend = process_time()

    # print out the result
    print('Time used:', str(tend - tstart))


def analyzers_log(settings, results):
    analyzers_dict = {}
    params_pop = ['plot_entry', 'plot_exit', 'limdays', 'printlog']
    for stratrun in results:
        for strat in stratrun:
            params = strat.params.__dict__
            [params.pop(param) for param in params_pop if param in params]
            analysis_value = {analyzer.__class__.__name__: analyzer.get_analysis() for analyzer in strat.analyzers}
            analysis_key = json.dumps(params, cls=NpEncoder)
            analyzers_dict.update({analysis_key: analysis_value})

    filepath = settings["opt_analyzer"]["path_log"].format(params['signal'])
    json.dump(analyzers_dict, open(filepath, "w"), sort_keys=True, indent=4)
    return None


def analyzers_read(settings, **kwargs):
    signal_opt = list(kwargs["signal"].keys())[0]
    objective_opt = settings["opt_analyzer"]["analyzer_opt"]

    output = {}
    output.update(kwargs)
    analyzers_keys = {
        "SQN": ["sqn"],
        "VWR": ["vwr"],
        # "TradeAnalyzer": ['len', 'long', 'lost', 'pnl', 'short', 'streak', 'total', 'won'],
        # "TimeDrawDown": ["maxdrawdown", "maxdrawdownperiod"]
    }

    filepath = settings["opt_analyzer"]["path_log"].format(signal_opt)
    analyzers = json.load(open(filepath, 'r'))
    analyzers_df = pandas.DataFrame()
    df = pandas.DataFrame(analyzers).T

    # filter params of analyzers
    for key, values in analyzers_keys.items():
        df_sample = df[key].apply(pandas.Series).loc[:, values]
        analyzers_df = pandas.concat([analyzers_df, df_sample], axis=1)

    best = analyzers_df.sort_values(by=objective_opt, ascending=False).head(1)
    best_index = json.loads(best.first_valid_index())
    signal = best_index.pop("signal")
    output["signal"][signal] = best_index

    output["signal"][signal]["analyzer_opt"] = {}
    output["signal"][signal]["analyzer_opt"][objective_opt] = best[objective_opt].values[0]
    # prototipe for multiobjective
    output["signal"][signal]["analyzer_opt"]["sqn"] = best["sqn"].values[0]
    # output["signal"][signal][objective_opt] = best[objective_opt].values[0]
    # output["signal"][signal]["sqn"] = best["sqn"].values[0]

    filename = settings["opt_analyzer"]["path_opt_parms"]
    with open(filename, "r+") as file:
        data = json.load(file)
        match_date = False
        for idx, row in enumerate(data):
            if (row.get("train").get("fromdate") == str(output.get("train").get("fromdate"))) &\
                    (row.get("train").get("todate") == str(output.get("train").get("todate"))):
                data[idx]["signal"][signal] = output["signal"][signal]
                match_date = True
                break
        if match_date == False:
            data.append(output)
        file.seek(0)
        # json.dump(data, file, indent=4, sort_keys=True, default=str)
        json.dump(data, file, indent=2, default=str)

    return None


def daterange_opt(settings, **kwargs):
    datapath = settings.get("opt_analyzer").get("datapath")
    dates_file_str = pandas.read_csv(datapath)["date"].unique()
    dates_file = [datetime.datetime.strptime(dt, "%Y.%m.%d") for dt in dates_file_str]

    fromdate = settings.get("opt_analyzer").get("fromdate")
    todate = settings.get("opt_analyzer").get("todate")
    daterange_opt = settings.get("opt_analyzer").get("daterange_opt")
    daterange_opt_train = settings.get("opt_analyzer").get("daterange_opt_train")

    if (fromdate == "") & (todate == ""):
        fromdate = dates_file[0]
        todate = dates_file[-1]
    elif (fromdate != "") & (todate == ""):
        fromdate = datetime.datetime.strptime(fromdate, "%Y.%m.%d")
        todate = dates_file[-1]
    elif (fromdate == "") & (todate != ""):
        todate = datetime.datetime.strptime(todate, "%Y.%m.%d")
        fromdate = dates_file[0]

    days_train = round(daterange_opt * daterange_opt_train)
    days_test = daterange_opt - days_train
    last_date_bin = fromdate
    dates = {}
    i = 0

    # while todate > last_date_bin + datetime.timedelta(days=daterange_opt):
    while dates_file.index(todate) > dates_file.index(last_date_bin) + daterange_opt:
        fromdate_bin_train = last_date_bin
        # todate_bin_train = fromdate_bin_train + datetime.timedelta(days=days_train)
        todate_bin_train_idx = dates_file.index(fromdate_bin_train) + days_train - 1
        todate_bin_train = dates_file[todate_bin_train_idx]

        # fromdate_bin_test = todate_bin_train + datetime.timedelta(days=1)
        fromdate_bin_test = dates_file[todate_bin_train_idx + 1]
        todate_bin_test_idx = dates_file.index(fromdate_bin_test) + days_test - 1
        todate_bin_test = dates_file[todate_bin_test_idx]
        # todate_bin_test = fromdate_bin_test + datetime.timedelta(days=days_test)

        # last_date_bin = todate_bin_test + datetime.timedelta(days=1)
        last_date_bin = dates_file[todate_bin_test_idx + 1]
        bin_dates = {"train": {"fromdate": fromdate_bin_train, "todate": todate_bin_train},
                     "test": {"fromdate": fromdate_bin_test, "todate": todate_bin_test}}
        dates.update({i: bin_dates})
        i += 1

    return dates


def params_ops_signals(settings, **kwargs):
    params_settings = settings["opt_params"]
    signals = kwargs.get("signals")
    dates = daterange_opt(settings)
    params_opt = []

    # update params_settings to range
    for signal, values in params_settings.items():
        for param, param_value in values.items():
            if len(param_value) > 1:
                params_settings[signal][param] = np.arange(*param_value)
            else:
                params_settings[signal][param] = param_value

    # update params for each date and signal
    for params in dates.values():
        for signal in signals:

            # Filter Signal to be used.
            params_signal = {key: params_settings.get(key) for key in params_settings if key in signal}
            params.update({"signal": params_signal})
            params_opt.append(params.copy())

    return params_opt


def params_ops_validate(settings, **kwargs):
    output = {}
    output.update(kwargs)
    signal_opt = list(kwargs["signal"].keys())[0]
    filename = settings["opt_analyzer"]["path_opt_parms"]

    with open(filename, "r") as file:
        data = json.load(file)
        for idx, row in enumerate(data):
            if (row.get("train").get("fromdate") == str(output.get("train").get("fromdate"))) & \
                (row.get("train").get("todate") == str(output.get("train").get("todate"))) & \
                (signal_opt in list(row.get("signal").keys())):
                file.close()
                return True
    return False


def main(settings, **kwargs):
    filename = settings["opt_analyzer"]["path_opt_parms"]

    # create file to store the output if there is none
    if os.path.isfile(filename) is False:
        json.dump([], open(filename, "w"), sort_keys=True, indent=4)

    # TODO: FIX SIGNALS OF: OBVSignal; EFISignal
    # params_signal = [params.get(key) for key in signals]
    # params_signal = params.get("SMASignal")
    # signals = ["SMASignal"]
    # signals = ["RSISignal"]
    # signals = ["SMASignal", "RSISignal"]
    # signals = ["MACDSignal", "RSISignal"]
    # signals = ["MACDSignal", "RSISignal", "WillRSignal", "ADXSignal", "StochasticSignal"]
    signals = ["MACDSignal", "RSISignal", "ADXSignal", "ElderForceIndexSignal"]

    params = params_ops_signals(settings, signals=signals)

    for params_opt in params:

        # validate if params already calculated, very helpful is case the code breaks
        if params_ops_validate(settings, **params_opt):
            continue

        else:
            # run optimization strategy
            runstrat_opt(settings, **params_opt)

            # select best parameters for given signal and save
            analyzers_read(settings, **params_opt)

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
