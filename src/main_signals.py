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

    opt_type = kwargs.pop("opt_type")
    filename, output_key = filename_key_opt_type(settings, opt_type=opt_type)
    # opt_type_dict = {
    #     "train": {"key": "output_train_key", "path": "path_output_train"},
    #     "test": {"key": "output_test_key", "path": "path_output_test"}
    # }
    # output_key = settings["opt_analyzer"][opt_type_dict[opt_type]["key"]]

    # update args of strategy
    args = parse_args(kwargs)

    # Create a cerebro entity
    cerebro = bt.Cerebro(stdstats=False,        # default kwarg: stdstats=True
                         # maxcpus=args.maxcpus,
                         # runonce=not args.no_runonce,
                         # exactbars=args.exactbars,
                         # optdatas=not args.no_optdatas,
                         # optreturn=not args.no_optreturn
                         )



    # Add a strategy
    cerebro.addstrategy(strategies.SignalsStrategy, **settings, **kwargs)

    # Get a data source path
    datapath = args.data

    # Pass it to the backtrader datafeed and add it to the cerebro
    data = bt.feeds.PandasData(dataname=pandasdatafeed(datapath, args=args),
                               fromdate=getattr(args, opt_type)["fromdate"], # fromdate=args.test["fromdate"],  # fromdate=args.fromdate,
                               todate=getattr(args, opt_type)["todate"]  # todate=args.test["todate"] # todate=args.todate)
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

    # Set Analyzer
    cerebro.addanalyzer(bt.analyzers.VWR, _name='vwr')  # VariabilityWeightedReturn
    cerebro.addanalyzer(bt.analyzers.SQN, _name='sqn')  # SystemQualityNumber.
    # cerebro.addanalyzer(bt.analyzers.TimeDrawDown, _name='timedrawdown')
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='tradeanalyzer')  # muito completo

    # Run over everything
    results = cerebro.run()

    # Extract/save analyzers
    analyzers_signals_log(settings, results, output_key=output_key, **kwargs)

    # clock the end of the process
    tend = process_time()

    # print out the result
    print('Time used:', str(tend - tstart))


def analyzers_signals_log(settings, results, **kwargs):
    output_key = kwargs.pop("output_key")
    analyzers_dict = kwargs
    for stratrun in results:
        analysis_value = {analyzer.__class__.__name__: analyzer.get_analysis() for analyzer in stratrun.analyzers}
        analyzers_dict.update({output_key: {"Signals": {"analyzer_opt": analysis_value}}})

    filepath = settings["opt_analyzer"]["path_log"].format('Signals')
    json.dump(analyzers_dict, open(filepath, "w"), indent=2, default=str)

    return None


def analyzers_signals_read(settings, **kwargs):
    filepath = settings["opt_analyzer"]["path_log"].format("Signals")
    output = json.load(open(filepath, 'r'))

    # opt_type = kwargs.pop("opt_type")
    filename, output_key = filename_key_opt_type(settings, opt_type="test")

    with open(filename, "r+") as file:
        data = json.load(file)
        match_date = False

        for idx, row in enumerate(data):
            if (row.get("test").get("fromdate") == str(output.get("test").get("fromdate"))) & \
                    (row.get("test").get("todate") == str(output.get("test").get("todate"))):
                data[idx]["output_train"] = output["output_train"]
                data[idx][output_key]["Signals"] = output[output_key]["Signals"]
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
    # opt_type = kwargs.pop("opt_type")
    filename, output_key = filename_key_opt_type(settings, opt_type="test")
    output = {}
    output.update(kwargs)
    # signal_opt = list(kwargs[output_key].keys())[0]

    if kwargs.get("override"):
        return False

    with open(filename, "r") as file:
        data = json.load(file)
        for idx, row in enumerate(data):
            if (row.get("test").get("fromdate") == str(output.get("test").get("fromdate"))) & \
                    (row.get("test").get("todate") == str(output.get("test").get("todate"))) & \
                    ("Signals" in list(row.get(output_key).keys())):
                file.close()
                return True
    return False


def filename_key_opt_type(settings, **kwargs):
    opt_type_dict = {
        "train": {"key": "output_train_key", "path": "path_output_train"},
        "test": {"key": "output_test_key", "path": "path_output_test"}
    }
    opt_type = kwargs.get("opt_type")
    days_train = settings["opt_analyzer"]["daterange_opt"]
    range_train = settings["opt_analyzer"]["daterange_opt_train"]
    filename = settings["opt_analyzer"][opt_type_dict[opt_type]["path"]].format(days_train, range_train)
    output_key = settings["opt_analyzer"][opt_type_dict[opt_type]["key"]]
    return filename, output_key


def main(settings, **kwargs):
    filename, output_key = filename_key_opt_type(settings, opt_type="test")
    filename_train, output_key_train = filename_key_opt_type(settings, opt_type="train")

    # create file to store the output if there is none
    if os.path.isfile(filename) is False:
        json.dump([], open(filename, "w"), sort_keys=True, indent=4)

    params = json.load(open(filename_train, "r"), object_hook=datetime_parser)

    for idx, params_opt in enumerate(params):

        # validate if params already calculated, very helpful is case the code breaks
        if params_output_validate(settings, override=False, opt_type="test", **params_opt):
            continue

        else:
            # run optimization strategy
            runstrat_signals(settings, opt_type="test", **params_opt)

            # read analyzers and save output
            analyzers_signals_read(settings, opt_type="test", **params_opt)

    return None


if __name__ == '__main__':
    settings = json.load(open("./src/settings.json"))

    # clock the start of the process
    tstart = process_time()

    # main script for test
    main(settings)

    # clock the end of the process
    tend = process_time()

    # print out the result
    print('Total Time used:', str(tend - tstart))
