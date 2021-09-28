from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import backtrader as bt  # Import the backtrader platform
# import datetime  # For datetime objects
# import os.path  # To manage paths
# import sys  # To find out the script name (in argv[0])
# import argparse
import os
import pandas
import glob
import json
import numpy as np
import dateutil.parser
import datetime  # For datetime objects

from src.datafeed import pandasdatafeed
from time import process_time
from src.args import parse_args
from backtrader.utils.py3 import range

from src import strategies
from src import main_opt



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


def runstrat_signals(settings, **kwargs):
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

    # update params of strategy

    # Add a strategy
    # cerebro.addstrategy(strategies.SignalsStrategy, **kwargs.get("signal"))
    cerebro.addstrategy(strategies.SignalsStrategy, **settings, **kwargs)

    # Get a data source path
    datapath = args.data

    # Pass it to the backtrader datafeed and add it to the cerebro
    data = bt.feeds.PandasData(dataname=pandasdatafeed(datapath, args=args),
                               fromdate=args.test["fromdate"],  # fromdate=args.fromdate,
                               todate=args.test["todate"])  # todate=args.todate)
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

    # Extract/save analyzers
    analyzers_signals_log(settings, results, **kwargs)

    # clock the end of the process
    tend = process_time()

    # print out the result
    print('Time used:', str(tend - tstart))


def analyzers_signals_log(settings, results, **kwargs):
    # analyzers_dict = {}
    analyzers_dict = kwargs
    for stratrun in results:
        analysis_value = {analyzer.__class__.__name__: analyzer.get_analysis() for analyzer in stratrun.analyzers}
        # analysis_key = json.dumps(kwargs, cls=NpEncoder, default=str)
        # analyzers_dict.update({analysis_key: analysis_value})
        analyzers_dict.update({"analyzers": analysis_value})

    filepath = settings["opt_analyzer"]["path_log"].format('Signals')
    json.dump(analyzers_dict, open(filepath, "w"), indent=2, default=str)

    return None


def analyzers_signals_read(settings, **kwargs):
    filepath = settings["opt_analyzer"]["path_log"].format("Signals")
    output = json.load(open(filepath, 'r'))

    # filename = settings["opt_analyzer"]["path_opt_parms"]
    filename = settings["opt_analyzer"]["path_output"]
    with open(filename, "r+") as file:
        data = json.load(file)
        match_date = False

        for idx, row in enumerate(data):
            if (row.get("train").get("fromdate") == str(output.get("train").get("fromdate"))) & \
                    (row.get("train").get("todate") == str(output.get("train").get("todate"))):
                data[idx]["analyzers"] = output["analyzers"]
                match_date = True
                break

        if match_date == False:
            data.append(output)

        file.seek(0, 0)
        json.dump(data, file, indent=2, default=str)
        file.close()

    return None


def datetime_parser(json_dict):
    for (key, value) in json_dict.items():
        try:
            json_dict[key] = dateutil.parser.parse(value)
        except (ValueError, AttributeError, TypeError):
            pass
    return json_dict


def params_output_validate(settings, **kwargs):
    output = {}
    output.update(kwargs)
    # signal_opt = list(kwargs["signal"].keys())[0]
    # filename = settings["opt_analyzer"]["path_opt_parms"]
    filename = settings["opt_analyzer"]["path_output"]

    if kwargs.get("ovverideskip"):
        return False

    with open(filename, "r") as file:
        data = json.load(file)
        for idx, row in enumerate(data):
            if (row.get("train").get("fromdate") == str(output.get("train").get("fromdate"))) & \
                (row.get("train").get("todate") == str(output.get("train").get("todate"))) & \
                ("analyzers" in list(row.keys())):
                file.close()
                return True
    return False


def remove_previous_records(settings, **kwargs):
    # filename = settings["opt_analyzer"]["path_opt_parms"]
    filename = settings["opt_analyzer"]["path_output"]

    if kwargs.get("ovverideskip"):
        return None

    with open(filename, "r+") as file:
        data = json.load(file)
        for idx, row in enumerate(data):
            remove_key = data[idx].pop("analyzers", None)

        file.seek(0, 0)
        json.dump(data, file, indent=2, default=str)
        file.close()

    return None


def main(settings, **kwargs):
    # remove_previous_records(settings, ovverideskip=False)
    remove_previous_records(settings, ovverideskip=True)

    filename = settings["opt_analyzer"]["path_opt_parms"]
    params = json.load(open(filename, "r"), object_hook=datetime_parser)

    for idx, params_opt in enumerate(params):

        # validate if params already calculated, very helpful is case the code breaks
        if params_output_validate(settings, ovverideskip=False, **params_opt):
            continue

        else:
            # run optimization strategy
            runstrat_signals(settings, **params_opt)

            # read analyzers and save output
            analyzers_signals_read(settings, **params_opt)

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
