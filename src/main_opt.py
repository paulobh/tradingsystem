from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import glob
import json

import pandas

from src import strategies
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
            analysis_key = json.dumps(params)
            analyzers_dict.update({analysis_key: analysis_value})

    filepath = settings["opt_analyzer"]["path_log"].format(params['signal'])
    # filepath = f"./data/analyzers_opt/analyzer_{params['signal']}.json"
    json.dump(analyzers_dict, open(filepath, "w"), sort_keys=True, indent=4)
    return None


def analyzers_read(settings, **kwargs):
    # filepath = "./data/analyzers_opt/analyzer_*.json"
    signal_opt = list(kwargs["signal"].keys())[0]
    filepath = settings["opt_analyzer"]["path_log"].format(signal_opt)

    analyzers_keys = {
        "SQN": ["sqn"],
        "VWR": ["vwr"],
        # "TradeAnalyzer": ['len', 'long', 'lost', 'pnl', 'short', 'streak', 'total', 'won'],
        # "TimeDrawDown": ["maxdrawdown", "maxdrawdownperiod"]
    }

    output = {
        "fromdate": kwargs.get("fromdate"),
        "todate": kwargs.get("todate"),
        "signal": {}
    }

    files = glob.glob(filepath)
    for file in files:
        analyzers = json.load(open(file, 'r'))
        analyzers = {tuple(json.loads(key).items()): value for key, value in analyzers.items()}
        analyzers_df = pandas.DataFrame()
        df = pandas.DataFrame(analyzers).T
        for key, values in analyzers_keys.items():
            df_sample = df[key].apply(pandas.Series).loc[:, values]
            analyzers_df = pandas.concat([analyzers_df, df_sample], axis=1)

        objective_opt = settings["opt_analyzer"]["analyzer_opt"]
        best = analyzers_df.sort_values(by=objective_opt, ascending=False).head(1)
        best_index = dict(best.first_valid_index())
        signal = best_index.pop("signal")
        output["signal"][signal] = best_index
        output["signal"][signal][objective_opt] = best[objective_opt].values[0]
        output["signal"][signal]["sqn"] = best["sqn"].values[0]

    filename = settings["opt_analyzer"]["path_opt_parms"]
    with open(filename, "r+") as file:
        data = json.load(file)
        match_date = False
        for idx, row in enumerate(data):
            if (row["fromdate"] == str(output["fromdate"])) & (row["todate"] == str(output["todate"])):
                data[idx]["signal"][signal] = output["signal"][signal]
                match_date = True
        if match_date == False:
            data.append(output)
        file.seek(0)
        # json.dump(data, file, indent=4, sort_keys=True, default=str)
        json.dump(data, file, indent=2, default=str)

    return None


def daterange_opt(settings, **kwargs):
    datapath = settings.get("opt_analyzer").get("datapath")

    fromdate = settings.get("opt_analyzer").get("fromdate")
    todate = settings.get("opt_analyzer").get("todate")
    daterange_opt = settings.get("opt_analyzer").get("daterange_opt")
    daterange_opt_train = settings.get("opt_analyzer").get("daterange_opt_train")

    if (fromdate == "") & (todate == ""):
        fromdate = datapath.split("_")[-3]
        fromdate = datetime.datetime.strptime(fromdate, "%Y.%m.%d")
        todate = datapath.split("_")[-2]
        todate = datetime.datetime.strptime(todate, "%Y.%m.%d")
    elif (fromdate != "") & (todate == ""):
        fromdate = datetime.datetime.strptime(fromdate, "%Y.%m.%d")
        # todate = fromdate + datetime.timedelta(days=daterange_opt)
        todate = datapath.split("_")[-2]
        todate = datetime.datetime.strptime(todate, "%Y.%m.%d")
    elif (fromdate == "") & (todate != ""):
        todate = datetime.datetime.strptime(todate, "%Y.%m.%d")
        # fromdate = todate - datetime.timedelta(days=daterange_opt)
        fromdate = datapath.split("_")[-3]
        fromdate = datetime.datetime.strptime(fromdate, "%Y.%m.%d")

    days_train = round(daterange_opt * daterange_opt_train)
    days_test = daterange_opt - days_train
    last_date_bin = fromdate
    dates = {}
    i = 0

    while todate > last_date_bin + datetime.timedelta(days=daterange_opt):
        fromdate_bin_train = last_date_bin
        todate_bin_train = fromdate_bin_train + datetime.timedelta(days=days_train)

        fromdate_bin_test = todate_bin_train + datetime.timedelta(days=1)
        todate_bin_test = fromdate_bin_test + datetime.timedelta(days=days_test)

        last_date_bin = todate_bin_test + datetime.timedelta(days=1)
        bin_dates = {"train": [fromdate_bin_train, todate_bin_train],
                     "test": [fromdate_bin_test, todate_bin_test]}
        dates.update({i: bin_dates})
        i += 1

    return dates


def main_opt(settings, **kwargs):
    params_settings = settings["opt_params"]
    # params_opt = settings["opt_analyzer"]
    filename = settings["opt_analyzer"]["path_opt_parms"]
    json.dump([], open(filename, "w"), sort_keys=True, indent=4)

    # TODO: FIX SIGNALS OF: OBVSignal; EFISignal
    # params_signal = [params.get(key) for key in signals]
    # params_signal = params.get("SMASignal")
    # signals = ["SMASignal"]
    # signals = ["RSISignal"]
    # signals = ["SMASignal", "RSISignal"]
    signals = ["MACDSignal", "RSISignal", "WillRSignal", "ADXSignal", "StochasticSignal"]
    dates = daterange_opt(settings)

    # allowed_keys = {'fromdate', 'todate'}
    # params.__dict__.update((k, v) for k, v in kwargs.items() if k in allowed_keys)

    for signal in signals:
        # Filter Signal to be used.
        params_signal = {key: params_settings.get(key) for key in params_settings if key in signal}

        # Fill range values.
        params_signal = {signal: {key: range(*params_settings.get(signal).get(key))
                                  for key in params_settings.get(signal)}
                         for signal in params_signal}

        params = {"signal": params_signal}

        for idx, date in dates.items():
            # TODO: ADICIONAR DATA DE TESTES PARA EVITAR DE CHAMR A FUNÇAO DATERANGE_OPT DEPOIS
            fromdate, todate = date["train"]
            params.update({"fromdate": fromdate, "todate": todate})
            # run optimization strategy
            runstrat_opt(settings, **params)
            # select best parameters for given signal and save
            analyzers_read(settings, **params)
    return None


if __name__ == '__main__':
    settings = json.load(open("./src/settings.json"))

    # runstrat()
    main_opt(settings)
