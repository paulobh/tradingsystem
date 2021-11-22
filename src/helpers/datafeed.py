# from __future__ import (absolute_import, division, print_function, unicode_literals)

import argparse
import pandas
import datetime  # For datetime objects
# from args import parse_args

# Import the backtrader platform
# import backtrader as bt
# import backtrader.feeds as btfeeds


def pandasdatafeed(datapath, **kwargs):
    args = kwargs.get('args', None)
    # args = parse_args()

    # Simulate the header row isn't there if noheaders requested
    skiprows = 1 if args.noheaders else 0
    header = None if args.noheaders else 0

    dataframe = pandas.read_csv(datapath,
                                # skiprows=skiprows,
                                # header=header,
                                # parse_dates=True,
                                parse_dates={'datetime': ['date', 'hour']},
                                index_col=0)
    # dataframe = dataframe.set_index('datetime')
    dataframe = dataframe.sort_index()
    data_cols = ['open', 'high', 'low', 'close', 'real_volume']
    dataframe = dataframe.loc[:, data_cols]
    dataframe = dataframe.rename(columns={"real_volume": "volume"})

    if not args.noprint:
        print('--------------------------------------------------')
        print(dataframe)
        print('--------------------------------------------------')

    return dataframe
