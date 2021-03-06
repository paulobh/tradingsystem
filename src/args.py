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
                        default='../samples/WIN$N_15M.csv',
                        help='Specific data to be read in')

    parser.add_argument('--fromdate', required=False, #default=None,
                        default=datetime.datetime(2012, 7, 1),
                        help='Starting date in YYYY-MM-DD format')

    parser.add_argument('--todate', required=False, #default=None,
                        # default=datetime.datetime(2012, 10, 1),
                        default=datetime.datetime(2012, 8, 1),
                        help='Ending date in YYYY-MM-DD format')

    parser.add_argument('--noheaders', action='store_true', default=False,
                        required=False,
                        help='Do not use header rows')

    parser.add_argument('--noprint', action='store_true', default=False,
                        help='Print the dataframe')

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

    # pgroup = parser.add_mutually_exclusive_group(required=True)
    #
    # pgroup.add_argument('--target-size', required=False, action='store_true',
    #                     help=('Use order_target_size'))
    #
    # pgroup.add_argument('--target-value', required=False, action='store_true',
    #                     help=('Use order_target_value'))
    #
    # pgroup.add_argument('--target-percent', required=False, action='store_true',
    #                     help=('Use order_target_percent'))

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
        return parser.parse_args(pargs)

    return parser.parse_args()