from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import argparse
import collections
import datetime  # For datetime objects

import backtrader as bt


MAINSIGNALS = collections.OrderedDict(
    (('longshort', bt.SIGNAL_LONGSHORT),
     ('longonly', bt.SIGNAL_LONG),
     ('shortonly', bt.SIGNAL_SHORT),)
)

EXITSIGNALS = {
    'longexit': bt.SIGNAL_LONGEXIT,
    'shortexit': bt.SIGNAL_LONGEXIT,
}


def parse_args(pargs=None):
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description='Sample for Signal concepts')

    # Data Feed
    parser.add_argument('--data', required=False,
                        default='./data/WIN$N_5M_2015.05.22_2021.01.22_.csv',
                        help='Specific data to be read in')
    parser.add_argument('--fromdate', required=False, #default=None,
                        default=datetime.datetime(2020, 11, 17),
                        help='Starting date in YYYY-MM-DD format')
    parser.add_argument('--todate', required=False, #default=None,
                        # default=datetime.datetime(2012, 10, 1),
                        default=datetime.datetime(2020, 11, 25),
                        help='Ending date in YYYY-MM-DD format')
    parser.add_argument('--noheaders', action='store_true', default=False,
                        required=False,
                        help='Do not use header rows')
    parser.add_argument('--noprint', action='store_true', default=False,
                        help='Print the dataframe')
    parser.add_argument('--writercsv', '-wcsv', action='store_true',
                        help='Tell the writer to produce a csv stream')

    # Strategy
    parser.add_argument('--cash', required=False, action='store',
                        type=float, default=1000000,
                        help='Cash to start with')
    parser.add_argument('--signal', required=False, action='store',
                        default=list(MAINSIGNALS)[0], choices=MAINSIGNALS,
                        help='Signal type to use for the main signal')
    parser.add_argument('--exitsignal', required=False, action='store',
                        default=None, choices=EXITSIGNALS,
                        help='Signal type to use for the exit signal')

    parser.add_argument('--exitperiod', required=False, action='store',
                        type=int, default=20,
                        help=('Period for the exit control ATR'))

    # Optimization
    parser.add_argument('--maxcpus', '-m', type=int, required=False, default=0,
                        help=('Number of CPUs to use in the optimization \n'
                              '  - 0 (default): use all available CPUs\n'
                              '  - 1 -> n: use as many as specified\n'))
    parser.add_argument('--no-runonce', action='store_true', required=False,
                        help='Run in next mode')
    parser.add_argument('--exactbars', required=False, type=int, default=0,
                        help=('Use the specified exactbars still compatible with preload\n'
                              '  0 No memory savings\n'
                              '  -1 Moderate memory savings\n'
                              '  -2 Less moderate memory savings\n'))
    parser.add_argument('--no-optdatas', action='store_true', required=False,
                        help='Do not optimize data preloading in optimization')
    parser.add_argument('--no-optreturn', action='store_true', required=False,
                        help='Do not optimize the returned values to save time')
    ## RSI
    parser.add_argument('--period_rsi_low', type=int, default=10, required=False,
                        help='RSI period range to optimize')
    parser.add_argument('--period_rsi_high', type=int, default=50, required=False,
                        help='RSI period range to optimize')
    ## SMA
    parser.add_argument('--ma_low', type=int, default=10, required=False,
                        help='SMA range low to optimize')
    parser.add_argument('--ma_high', type=int, default=14, required=False,
                        help='SMA range high to optimize')
    parser.add_argument('--m1_low', type=int, default=12, required=False,
                        help='MACD Fast MA range low to optimize')
    parser.add_argument('--m1_high', type=int, default=15, required=False,
                        help='MACD Fast MA range high to optimize')
    parser.add_argument('--m2_low', type=int, default=26, required=False,
                        help='MACD Slow MA range low to optimize')
    parser.add_argument('--m2_high', type=int, default=28, required=False,
                        help='MACD Slow MA range high to optimize')
    parser.add_argument('--m3_low', type=int, default=9, required=False,
                        help='MACD Signal range low to optimize')
    parser.add_argument('--m3_high', type=int, default=12, required=False,
                        help='MACD Signal range high to optimize')

    # Cerebro
    parser.add_argument('--cerebro', required=False, default='',
                        metavar='kwargs', help='kwargs in key=value format')
    parser.add_argument('--broker', required=False, default='',
                        metavar='kwargs', help='kwargs in key=value format')
    parser.add_argument('--sizer', required=False, default='',
                        metavar='kwargs', help='kwargs in key=value format')
    parser.add_argument('--strat', required=False, default='',
                        metavar='kwargs', help='kwargs in key=value format')

    # Plot options
    parser.add_argument('--plot', '-p', nargs='?', required=False, default=True,
                        metavar='kwargs', const=True,
                        help=('Plot the read data applying any kwargs passed\n'
                              '\n'
                              'For example:\n'
                              '\n'
                              '  --plot style="candle" (to plot candles)\n'))

    if pargs is not None:
        print("detected pargs \n")
        args = parser.parse_args()
        args.__dict__.update(pargs)
        return args

    args = parser.parse_args()
    print("not detected pargs \n")
    return args
