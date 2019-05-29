from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import argparse
import pandas
import datetime  # For datetime objects

# Import the backtrader platform
import backtrader as bt
import backtrader.feeds as btfeeds

def pandasdatafeed(datapath):
    args = parse_args()

    # Simulate the header row isn't there if noheaders requested
    skiprows = 1 if args.noheaders else 0
    header = None if args.noheaders else 0

    dataframe = pandas.read_csv(datapath,
                                skiprows=skiprows,
                                header=header,
                                # parse_dates=True,
                                parse_dates={'datetime': ['date', 'hour']},
                                index_col=0)
    dataframe = dataframe.set_index('datetime').sort_index()
    data_cols = ['open', 'high', 'low', 'close', 'real_volume']
    dataframe = dataframe.loc[:, data_cols]
    dataframe = dataframe.rename(columns={"real_volume": "volume"})

    if not args.noprint:
        print('--------------------------------------------------')
        print(dataframe)
        print('--------------------------------------------------')

    return dataframe

def parse_args(pargs=None):

    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description='Pandas test script')

    # parser.add_argument('--noheaders', action='store_true', default=False,
    #                     required=False,
    #                     help='Do not use header rows')
    #
    # parser.add_argument('--noprint', action='store_true', default=False,
    #                     help='Print the dataframe')

    parser.add_argument('--data', required=False,
                        default='../resources/WIN$N_15M.csv',
                        help='Data to be read in')

    # parser.add_argument('--maxcpus', required=False, action='store',
    #                     default=None, type=int,
    #                     help='Limit the numer of CPUs to use')
    #
    # parser.add_argument('--optreturn', required=False, action='store_true',
    #                     help='Return reduced/mocked strategy object')

    return parser.parse_args(pargs)