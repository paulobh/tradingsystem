# import os
# import glob
import pandas
# import datetime

from .context import data_analysis as da


def test_list_data_files():
    output = da.list_data_files()
    assert isinstance(output, dict)
    assert len(output.keys()) > 0


def test_filter_overlapping_dates():
    files = da.list_data_files()
    file1 = files["1M"][0]
    file2 = files["3M"][0]
    dates_duplicated = da.filter_overlapping_dates(file1, file2)
    assert len(dates_duplicated) is 0
    assert isinstance(dates_duplicated, list)

    file2 = files["10M"][0]
    dates_duplicated = da.filter_overlapping_dates(file1, file2)
    assert len(dates_duplicated) > 0
    assert isinstance(dates_duplicated, list)


def test_filter_overlapping_files():
    df_input = da.list_data_files()
    output = da.filter_overlapping_files(df_input)
    assert isinstance(output, dict)


def test_filter_date_df():
    files = da.list_data_files()
    file1 = files["1M"][0]
    file2 = files["10M"][0]
    dates_overlapping = da.filter_overlapping_dates(file1, file2)
    df1 = pandas.read_csv(file1)
    output = da.filter_date_df(dates_overlapping, df1)
    assert isinstance(output, pandas.DataFrame)
    assert len(output) > 0


def test_format_hour():
    data = {
        'date': {0: '2015.08.12', 1: '2015.08.12', 2: '2015.08.12', 3: '2015.08.12'},
        'hour': {0: '09:05:00', 1: '09:01:00', 2: '17:02:00', 3: '9:03:00'}}
    df_input= pandas.DataFrame(data=data)
    data = {
        'date': {0: '2015.08.12', 1: '2015.08.12', 2: '2015.08.12', 3: '2015.08.12'},
        'hour': {0: '09:01:00', 1: '09:03:00', 2: '09:05:00', 3: '17:02:00'}}
    df_expected = pandas.DataFrame(data=data)
    output = da.format_hour(df_input)
    assert output.equals(df_expected)


def test_filter_overlapping_files_dfs():
    files = da.list_data_files()
    file1 = files["1M"][0]
    file2 = files["10M"][0]
    output = da.filter_overlapping_files_dfs(file1, file2)
    assert len(output) == 2
    assert len(output[0]) > 0

    file1 = files["1M"][0]
    file2 = files["3M"][0]
    output = da.filter_overlapping_files_dfs(file1, file2)
    assert len(output) == 2
    assert len(output[0]) == 0


def test_filter_time_match():
    files = da.list_data_files()
    file1 = files["1M"][0]
    file2 = files["10M"][0]
    output = da.filter_time_match(file1, file2)
    assert len(output) is 2


def test_compare_candles_frequencies():
    files = da.list_data_files()
    file1 = files["1M"][0]
    file2 = files["10M"][0]
    output = da.compare_candles_frequencies(file1, file2)
    assert len(output) is 5
    assert all(isinstance(n, int) for n in list(output[0]))

    file1 = files["1M"][1]
    file2 = files["10M"][0]
    output = da.compare_candles_frequencies(file1, file2)
    assert len(output) is 5
    assert all(isinstance(n, int) for n in list(output[0]))


def test_format_df_candles():
    files = da.list_data_files()
    file1 = files["1M"][0]
    file2 = files["10M"][0]
    candles, df1, df2, time_match_df1, time_match_df2 = da.compare_candles_frequencies(file1, file2)
    output = da.format_df_candles(df1, time_match_df1, candles)
    assert isinstance(output, pandas.DataFrame)
    assert len(output) > 0


def test_candles_analysis():
    files = da.list_data_files()
    # file1 = files["1M"][0]
    # file2 = files["10M"][0]
    # candles, df1, df2, time_match_df1, time_match_df2 = da.compare_candles_frequencies(file1, file2)
    # df = da.format_df_candles(df1, time_match_df1, candles)
    output = da.candles_analysis(files)
    assert output is None


# def test_plot_df():
#     files = da.list_data_files()
#     file1 = files["1M"][0]
#     file2 = files["10M"][0]
#     candles, df1, df2, time_match_df1, time_match_df2 = da.compare_candles_frequencies(file1, file2)
#     df = da.format_df_candles(df1, time_match_df1, candles)
#     assert False


