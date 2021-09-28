""" Data analysis functions for source files
associated with : `data_analysis.ipynb`
"""

import os
import glob
import pandas
import datetime

# confirmar local de execução do código
# os.chdir('..')
# print(os.getcwd())


def list_data_files(data_path ="./data/*.csv"):
    """List available file to do the data analysis and group in a dict according the data frequency.

    Files should have the following structure:
        WIN$N_10M_2013.11.08_2021.01.22_.csv
        {ativo}_{frequencia}_{data_inicio}_{data_fim}_.csv

    Parameters
    ----------
    data_path: str
        path to look for the files.

    Returns
    -------
    dict_files: dict
        dict with frequencies as keys and list of files as values.

    Examples
    --------
    >>> list_data_files()
    {'10M': ['./data\\WIN$N_10M_2013.11.08_2021.01.22_.csv'],
    '15M': ['./data\\WIN$N_15M_2012.04.20_2021.01.22_.csv']}

    """
    dict_files = {}
    files = glob.glob(data_path)
    for file in files:
        freq = file.split(".")[1].split("_")[1]
        if freq in list(dict_files.keys()):
            dict_files[freq].append(file)
        else:
            dict_files[freq] = [file]
    return dict_files


def filter_overlapping_dates(file1, file2):
    """Filtra dados que possuem datas sobrepostas.

    Parameters
    ----------
    file1: str
        CSV filepath.
    file2: str
        CSV filepath.

    Returns
    -------
    duplicated: list
        list with overlapping dates on both input files.

    Examples
    --------
    >>> file1 = './data/WIN$N_1M_2015.08.12_2015.12.30_.csv',
    >>> file2 = './data/WIN$N_10M_2013.11.08_2021.01.22_.csv'
    >>> filter_overlapping_dates(file1, file2)
    ['2015.08.12', '2015.08.13', '2015.08.14', ... '2015.12.29', '2015.12.30']

    """
    df1 = pandas.read_csv(file1)
    df2 = pandas.read_csv(file2)
    dates_df1 = df1["date"].drop_duplicates().reset_index(drop=True)
    dates_df2 = df2["date"].drop_duplicates().reset_index(drop=True)
    dates = dates_df1.append(dates_df2).reset_index(drop=True)
    duplicated = dates[dates.duplicated()].reset_index(drop=True)
    return list(duplicated)


def filter_overlapping_files(files):
    """Filter combinations of overlapping files.

    Uses as base comparing file the one with lowest frequency.

    Parameters
    ----------
    files: dict
         dict with frequencies as keys and list of files as values.

    Returns
    -------
    dict_files_all: dict
        dict with combination frequencies as keys and list of lists with files combinations as values.

    Examples
    --------
    >>> files = list_data_files()
    >>> filter_overlapping_files(files)
    {'1M_10M': [
        ['./data\\WIN$N_1M_2015.08.12_2015.12.30_.csv', './data\\WIN$N_10M_2013.11.08_2021.01.22_.csv'],
        ['./data\\WIN$N_1M_2016.08.02_2016.11.18_.csv', './data\\WIN$N_10M_2013.11.08_2021.01.22_.csv'],
        ['./data\\WIN$N_1M_2019.11.21_2021.01.20_.csv', './data\\WIN$N_10M_2013.11.08_2021.01.22_.csv']],
    '1M_15M': [
        ['./data\\WIN$N_1M_2015.08.12_2015.12.30_.csv', './data\\WIN$N_15M_2012.04.20_2021.01.22_.csv'],
        ['./data\\WIN$N_1M_2016.08.02_2016.11.18_.csv', './data\\WIN$N_15M_2012.04.20_2021.01.22_.csv'],
        ['./data\\WIN$N_1M_2019.11.21_2021.01.20_.csv', './data\\WIN$N_15M_2012.04.20_2021.01.22_.csv']],
    ...
    '1M_3M': [['./data\\WIN$N_1M_2019.11.21_2021.01.20_.csv', './data\\WIN$N_3M_2018.05.25_2021.01.22_.csv']]
     }

    """
    keys = list(files.keys())
    base = min([key.replace("M", "") for key in files.keys()])
    base = str(base) + "M"
    keys.remove(base)
    base_files = files[base]

    dict_files_all = {}
    for key in keys:
        file_keys = files[key]
        for file_key in file_keys:
            for file_base in base_files:
                dates_overlapping = filter_overlapping_dates(file_base, file_key)
                if len(dates_overlapping) > 0:
                    list_files = [file_base, file_key]
                    combination = base + "_" + key
                    if combination in dict_files_all.keys():
                        dict_files_all[combination].append(list_files)
                    else:
                        dict_files_all[combination] = [list_files]
    return dict_files_all


def format_hour(df):
    """Ajuste do formato da hora.

    Sometimes the hour need to be proper formatted to be properly sorted.
    It should be "09:00:00" and not "9:00:00".

    Parameters
    ----------
    df: pandas.Dataframe
        Dataframe with columns "date" and "hour"

    Returns
    -------
    df: pandas.Dataframe
        Dataframe with proper Hour format.

    Examples:
    --------
    >>> print(df)
            date      hour   open   high    low  close  real_volume  tick_volume
    0  2015.08.12  09:00:00  50280  50430  50255  50405          976          217
    1  2015.08.12  09:01:00  50405  50440  50335  50400         1589          445
    2  2015.08.12  09:02:00  50395  50410  50355  50355          465          102
    ...
    997  2015.08.12  18:30:00  50395  50410  50355  50355          465          102
    998  2015.08.12  9:03:00  50350  50360  50320  50325          474          150
    999  2015.08.12  9:04:00  50325  50330  50090  50190         2078          747
    >>> df = format_hour(df)
    >>> print(df)
            date      hour   open   high    low  close  real_volume  tick_volume
    0  2015.08.12  09:00:00  50280  50430  50255  50405          976          217
    1  2015.08.12  09:01:00  50405  50440  50335  50400         1589          445
    2  2015.08.12  09:02:00  50395  50410  50355  50355          465          102
    3  2015.08.12  09:03:00  50350  50360  50320  50325          474          150
    4  2015.08.12  09:04:00  50325  50330  50090  50190         2078          747
    ...
    999  2015.08.12  18:30:00  50395  50410  50355  50355          465          102

    """
    for idx, row in enumerate(df["hour"]):
        hour = row.split(":")[0]
        if len(hour) == 1:
            hour = "0" + hour
            hour = ":".join([hour, ":".join(row.split(":")[1:])])
            df.loc[idx, "hour"] = hour
    df = df.drop_duplicates()
    df = df.sort_values(by=["date", "hour"]).reset_index(drop=True)
    return df


def filter_date_df(date_time, df, var="date"):
    """Filtrar dataframe para uma dada lista de datas.

    Parameters
    ----------
    date_time: list
        list with dates.
    df: pandas.Dataframe

    var: str
        column to filter, default value is "date" but can be adaptable for other ones.

    Returns
    -------
    df_filter: pandas.Dataframe

    Examples
    --------
    >>> file1 = './data/WIN$N_1M_2015.08.12_2015.12.30_.csv',
    >>> file2 = './data/WIN$N_10M_2013.11.08_2021.01.22_.csv'
    >>> dates = filter_overlapping_dates(file1, file2)
    >>> df1 = pandas.read_csv(file1)
    >>> filter_date_df(dates_overlapping, df1).head()
            date      hour   open   high    low  close  real_volume  tick_volume
    0  2015.08.12  09:00:00  50280  50430  50255  50405          976          217
    1  2015.08.12  09:01:00  50405  50440  50335  50400         1589          445
    2  2015.08.12  09:02:00  50395  50410  50355  50355          465          102
    3  2015.08.12  09:03:00  50350  50360  50320  50325          474          150
    4  2015.08.12  09:04:00  50325  50330  50090  50190         2078          747

    """
    filters = [True if date in date_time else False for date in df[var]]
    df_filter = df[filters]
    df_filter = df_filter.drop(columns=["spread"], errors="ignore")
    df_filter = df_filter.dropna().drop_duplicates()
    df_filter = df_filter.sort_values(by=["date", "hour"])
    df_filter = df_filter.reset_index(drop=True)
    df_filter = format_hour(df_filter)
    return df_filter


def filter_overlapping_files_dfs(file1, file2):
    """Filter overlapping between 2 files.

    Parameters
    ----------
    file1: str
        CSV filepath.
    file2: str
        CSV filepath.

    Returns
    -------
    df1_filter: pandas.Dataframe
    df2_filter: pandas.Dataframe

    Examples
    --------
    >>> file1 = './data/WIN$N_1M_2015.08.12_2015.12.30_.csv',
    >>> file2 = './data/WIN$N_10M_2013.11.08_2021.01.22_.csv'
    >>> df1_filter, df2_filter = filter_overlapping_files_dfs(file1, file2)
    >>> print(df1_filter.head())
             date      hour   open   high    low  close  real_volume  tick_volume
    0  2015.08.12  09:00:00  50280  50430  50255  50405          976          217
    1  2015.08.12  09:01:00  50405  50440  50335  50400         1589          445
    2  2015.08.12  09:02:00  50395  50410  50355  50355          465          102
    3  2015.08.12  09:03:00  50350  50360  50320  50325          474          150
    4  2015.08.12  09:04:00  50325  50330  50090  50190         2078          747
    >>> print(df2_filter.head())
             date      hour   open   high    low  close  real_volume  tick_volume
    0  2015.08.12  09:00:00  50280  50440  50030  50260         8559         2938
    1  2015.08.12  09:10:00  50260  50375  50230  50260         5491         2189
    2  2015.08.12  09:20:00  50265  50305  50120  50140         4973         2142
    3  2015.08.12  09:30:00  50145  50155  49585  49665        15082         6077
    4  2015.08.12  09:40:00  49675  49685  49550  49650         6575         2504

    """
    df1 = pandas.read_csv(file1)
    df2 = pandas.read_csv(file2)
    dates_overlapping = filter_overlapping_dates(file1, file2)
    df1_filter = filter_date_df(dates_overlapping, df1)
    df2_filter = filter_date_df(dates_overlapping, df2)
    return df1_filter, df2_filter


def filter_time_match(file1, file2):
    """Create index match for given files.

    Parameters
    ----------
    file1: str
        CSV filepath.
    file2: str
        CSV filepath.

    Returns
    -------
    time_match_df1: pandas.core.series.Series
    time_match_df2: pandas.core.series.Series

    Examples
    --------
    >>> file1 = './data/WIN$N_1M_2015.08.12_2015.12.30_.csv',
    >>> file2 = './data/WIN$N_10M_2013.11.08_2021.01.22_.csv'
    >>> time_match_df1, time_match_df2 = filter_time_match(file1, file2)
    >>> print(time_match_df1)
    (0, 0) (1, 0) (2, 0) (3, 0) (4, 0) (5, 0) (6, 0) (7, 0) (8, 0) (9, 0) (10, 1) (11, 1) (12, 1)...
    >>> print(time_match_df2)
    (0, (0, 1, 2, 3, 4, 5, 6, 7, 8, 9)) (1, (10, 11, 12, 13, 14, 15, 16, 17, 18, 19)) ...

    """
    freq1 = int(file1.split(".")[1].split("_")[1].replace("M", ""))
    freq2 = int(file2.split(".")[1].split("_")[1].replace("M", ""))
    df1, df2 = filter_overlapping_files_dfs(file1, file2)

    dt1 = pandas.to_datetime(df1["date"] + " " + df1["hour"])
    dt2 = pandas.to_datetime(df2["date"] + " " + df2["hour"])

    dt_delta = datetime.timedelta(minutes=freq2 - freq1)
    time_match_df1 = dt1.copy()
    time_match_df2 = dt2.copy()
    for idx, dt in dt2.items():
        match = dt1[(dt1 >= dt) & (dt1 <= dt + dt_delta)]
        time_match_df1[match.index] = idx
        time_match_df2[idx] = 0
        time_match_df2[idx] = tuple(match.index)

    time_match_df2[time_match_df2.apply(len) != 10]
    return time_match_df1, time_match_df2


def compare_candles_frequencies(file1, file2):
    """Comparar arquivos sobrepostos de frequencias diferentes.

    candles types:
    1 : Close > Open & Low is before High
    2 : Close < Open & Low is after High
    3 : Close > Open & Low is after High
    4 : Close < Open & Low is before High

    Parameters
    ----------
    file1: str
        CSV filepath.
    file2: str
        CSV filepath.

    Returns
    -------
    candles: pandas.core.series.Series
        series with candles types.
    df1: pandas.Dtaframe
        dataframe with smaller frequency data.
    df2: pandas.Dtaframe
        dataframe with larger frequency data.
    time_match_df1: pandas.core.series.Series
        series with match index for smaller frequency dataset
    time_match_df2: pandas.core.series.Series
        series with match index for larger frequency dataset

    Examples
    --------
    >>> file1 = './data/WIN$N_1M_2015.08.12_2015.12.30_.csv'
    >>> file2 = './data/WIN$N_10M_2013.11.08_2021.01.22_.csv'
    >>> candles, df1, df2, time_match_df1, time_match_df2 = compare_candles_frequencies(file1, file2)
    >>> print(candles)
    (0, 2) (1, 0) (2, 2) (3, 2) (4, 2) (5, 4) (6, 2) (7, 4) (8, 1) (9, 2) (10, 2) (11, 1) (12, 1) (13, 2)
    >>> print(df1.head())
             date      hour   open   high    low  close  real_volume  tick_volume
    0  2015.08.12  09:00:00  50280  50430  50255  50405          976          217
    1  2015.08.12  09:01:00  50405  50440  50335  50400         1589          445
    2  2015.08.12  09:02:00  50395  50410  50355  50355          465          102
    3  2015.08.12  09:03:00  50350  50360  50320  50325          474          150
    4  2015.08.12  09:04:00  50325  50330  50090  50190         2078          747
    >>> print(df2.head())
             date      hour   open   high    low  close  real_volume  tick_volume
    0  2015.08.12  09:00:00  50280  50440  50030  50260         8559         2938
    1  2015.08.12  09:10:00  50260  50375  50230  50260         5491         2189
    2  2015.08.12  09:20:00  50265  50305  50120  50140         4973         2142
    3  2015.08.12  09:30:00  50145  50155  49585  49665        15082         6077
    4  2015.08.12  09:40:00  49675  49685  49550  49650         6575         2504
    >>> print(time_match_df1)
    (0, 0) (1, 0) (2, 0) (3, 0) (4, 0) (5, 0) (6, 0) (7, 0) (8, 0) (9, 0) (10, 1) (11, 1) (12, 1) (13, 1) (14, 1)...
    >>> print(time_match_df2)
    (0, (0, 1, 2, 3, 4, 5, 6, 7, 8, 9)) (1, (10, 11, 12, 13, 14, 15, 16, 17, 18, 19)) ...

    """
    df1, df2 = filter_overlapping_files_dfs(file1, file2)
    time_match_df1, time_match_df2 = filter_time_match(file1, file2)
    candles = time_match_df2.copy()
    for idx, row in df2.iterrows():
        if (time_match_df2[idx] == ()) or (len(time_match_df2[idx]) < 3):
            candles[idx] = 0
            continue
        p_open, p_high, p_low, p_close = row[["open", "high", "low", "close"]]
        df1_sample = df1.loc[list(time_match_df2[idx]), :]
        if (p_high not in list(df1_sample["high"])) or (p_low not in list(df1_sample["low"])):
            candles[idx] = 0
            continue
        i_high = df1_sample[df1_sample["high"] == p_high].index[0]
        i_low = df1_sample[df1_sample["low"] == p_low].index[0]
        if (p_close > p_open) & (i_high > i_low):
            candles[idx] = 1
        elif (p_close < p_open) & (i_high < i_low):
            candles[idx] = 2
        elif (p_close > p_open) & (i_high < i_low):
            candles[idx] = 3
        elif (p_close < p_open) & (i_high > i_low):
            candles[idx] = 4
        else:
            candles[idx] = 0
    # time_match_df2.value_counts()
    return candles, df1, df2, time_match_df1, time_match_df2


def format_df_candles(df, time_match_df, candles):
    """Format dataframe to aggregate more information.

    Parameters
    ----------
    df: pandas.Dataframe
    time_match_df: pandas.core.series.Series
    candles: pandas.core.series.Series
    candle_type: int

    Returns
    -------
    df: pandas.Dataframe

    Examples
    --------
    >>> file1 = './data/WIN$N_1M_2015.08.12_2015.12.30_.csv'
    >>> file2 = './data/WIN$N_10M_2013.11.08_2021.01.22_.csv'
    >>> candles, df1, df2, time_match_df1, time_match_df2 = compare_candles_frequencies(file1, file2)
    >>> df = format_df_candles(df1, time_match_df1, candles, candle_type=1)
    >>> print(df.head(12))
              date      hour   open   high  ...  tick_volume  id  match  candle
    0   2015.08.12  09:00:00  50280  50430  ...          217   0      0       2
    1   2015.08.12  09:01:00  50405  50440  ...          445   1      0       2
    2   2015.08.12  09:02:00  50395  50410  ...          102   2      0       2
    3   2015.08.12  09:03:00  50350  50360  ...          150   3      0       2
    4   2015.08.12  09:04:00  50325  50330  ...          747   4      0       2
    5   2015.08.12  09:05:00  50185  50195  ...          439   5      0       2
    6   2015.08.12  09:06:00  50130  50190  ...          321   6      0       2
    7   2015.08.12  09:07:00  50175  50225  ...          167   7      0       2
    8   2015.08.12  09:08:00  50210  50220  ...           96   8      0       2
    9   2015.08.12  09:09:00  50220  50275  ...          254   9      0       2
    10  2015.08.12  09:10:00  50260  50320  ...          579   0      1       0
    11  2015.08.12  09:11:00  50310  50340  ...          313   1      1       0
    [12 rows x 11 columns]

    """
    ids = [0]
    for idx, value in enumerate(time_match_df.diff()[:-1]):
        if value != 0:
            ids.insert(idx, 0)
        else:
            ids.insert(idx, ids[idx - 1] + 1)
    df["id"] = ids
    df["match"] = time_match_df
    df["candle"] = [candles[value] for value in df["match"]]
    return df


def candles_analysis(files):
    dict_files = filter_overlapping_files(files)
    df = pandas.DataFrame()
    for key, values in dict_files.items():
        for value in values:
            date_range = "_".join(value[0].split("_")[2:4])
            file1, file2 = value
            candles, df1, df2, time_match_df1, time_match_df2 = compare_candles_frequencies(file1, file2)
            candles_counts = candles.value_counts()
            candles_index = pandas.Series([key, date_range], index=["frequencies", "date_range"])
            candles_index = candles_index.append(candles_counts)
            df = df.append(candles_index.T, ignore_index=True)

    df = df.set_index(["frequencies", "date_range"])
    df.to_csv("./samples/candles_analisys.csv")
    return df


# def plot_df(df):
# def plot_df(df):
#     return None


# import plotly.graph_objects as go
# fig = go.Figure(data=go.Bar(y=[2, 3, 1]))
# fig.write_html('first_figure.html', auto_open=True)
# fig.show()
# fig = go.FigureWidget(data=go.Bar(y=[2, 3, 1]))
# fig

