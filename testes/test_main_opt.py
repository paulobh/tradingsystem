import os

# import glob
import pandas
import json
import datetime
import numpy as np

from testes import context
from src import main_opt as opt

def test_analyzers_read():
    settings = json.load(open("./src/settings.json"))
    kwargs = {
        'train': {'fromdate': datetime.datetime(2015, 5, 22, 0, 0), 'todate': datetime.datetime(2015, 6, 8, 0, 0)},
        'test': {'fromdate': datetime.datetime(2015, 6, 9, 0, 0), 'todate': datetime.datetime(2015, 6, 13, 0, 0)},
        'signal': {'MACDSignal': {'period_me1': np.array([10, 15]), 'period_me2': np.array([20, 25]),
                                  'period_signal': np.array([5, 10]), 'period_atr': np.array([50, 70, 90]),
                                  'atrdist': np.array([0.75, 1., 1.25, 1.5, 1.75]),
                                  'atrprofit': np.array([0.75, 1., 1.25, 1.5, 1.75]), 'time_start': [[9, 0]],
                                  'time_stop': [[17, 0]]}}}

    output = opt.analyzers_read(settings, **kwargs)
    assert False
    

def test_analyzer_opt():
    settings = json.load(open("./src/settings.json"))
    kwargs = {
        'train': {'fromdate': datetime.datetime(2015, 5, 22, 0, 0), 'todate': datetime.datetime(2015, 6, 8, 0, 0)},
        'test': {'fromdate': datetime.datetime(2015, 6, 9, 0, 0), 'todate': datetime.datetime(2015, 6, 13, 0, 0)},
        'signal': {'MACDSignal': {'period_me1': np.array([10, 15]), 'period_me2': np.array([20, 25]),
                                  'period_signal': np.array([5, 10]), 'period_atr': np.array([50, 70, 90]),
                                  'atrdist': np.array([0.75, 1., 1.25, 1.5, 1.75]),
                                  'atrprofit': np.array([0.75, 1., 1.25, 1.5, 1.75]), 'time_start': [[9, 0]],
                                  'time_stop': [[17, 0]]}}}
    output = opt.analyzers_read(settings, **kwargs)
    assert False


def test_params_ops_validate():
    settings = json.load(open("./src/settings.json"))
    kwargs = {
         'train': {'fromdate': datetime.datetime(2015, 5, 22, 0, 0), 'todate': datetime.datetime(2015, 6, 8, 0, 0)},
         'test': {'fromdate': datetime.datetime(2015, 6, 9, 0, 0), 'todate': datetime.datetime(2015, 6, 13, 0, 0)},
         'signal': {'MACDSignal': {'period_me1': np.array([10, 15]), 'period_me2': np.array([20, 25]),
                                   'period_signal': np.array([5, 10]), 'period_atr': np.array([50, 65]),
                                   'atrdist': np.array([0.8, 1., 1.2]), 'atrprofit': np.array([0.8, 1., 1.2]),
                                   'time_start': [[9, 0]], 'time_stop': [[17, 0]]}}}

    output = opt.params_ops_validate(settings, **kwargs)
    assert output is True


def test_validate_null_data():
    settings = json.load(open("./src/settings.json"))
    datapath = settings.get("opt_analyzer").get("datapath")
    df = pandas.read_csv(datapath)

    # date_start_slice = "2017.05.19"
    date_start_slice = "2016.11.01"
    filter_dt_start = df.date >= date_start_slice
    df = df[filter_dt_start]

    # date_end_slice = "2017.06.02"
    date_end_slice = "2016.11.24"
    filter_dt_end = df.date <= date_end_slice
    df = df[filter_dt_end]
    return


    
    
