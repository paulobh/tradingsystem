""" Organize source data series

"""
import os
import glob
import pandas

from datetime import datetime


def list_data_files():
    dict_files = {}
    files = glob.glob("./data/*.csv")
    for file in files:
        freq = file.split(".")[1].split("_")[1]
        if freq in list(dict_files.keys()):
            dict_files[freq].append(file)
        else:
            dict_files[freq] = [file]
    return dict_files


def read_csv(filepath):
    df = pandas.read_csv(filepath)
    columns = [s.strip() for s in df.columns]
    df.columns = columns
    df = df.drop_duplicates()
    return df


def split_date_column(df):
    """Split date column into date and time, and reorder columns.

    Parameters
    ----------
    df: pandas.Dataframe

    Returns
    -------
    df: pandas.Dataframe

    Example
    -------
    >>> filename= "./data/WIN$N_1M_2021.01.20_2020.04.24.csv"
    >>> df = read_csv(filename)
    >>> df = split_date_column(df)
    """
    columns = [s.strip() for s in df.columns]
    if "hour" in columns:
        return df
    elif "date" in columns:
        df[["date", "hour"]] = df['date'].str.split(' ', 1, expand=True)
        cols = df.columns
        cols = cols[:-1].insert(1, cols[-1])
        return df[cols]


def get_start_end_dt(df):
    dates = sorted(list(df["date"].unique()))
    date_start = dates[0]
    date_end = dates[-1]
    return date_start, date_end


def process_overlapping_dfs(df1, df2):
    df = pandas.concat([df1, df2], ignore_index=True)
    df = df.drop_duplicates()
    df = df.sort_values(by=["date", "hour"])
    df = df.reset_index(drop=True)
    return df


def split_date_dfs(df, days_split=30):
    idx_split = []
    for idx, date in df.loc[1:, "date"].drop_duplicates().items():
        date_idx = datetime.strptime(date, "%Y.%m.%d").date()
        date_idx_1 = datetime.strptime(df.loc[idx-1, "date"], "%Y.%m.%d").date()
        diff_date = abs(date_idx - date_idx_1).days
        if diff_date > days_split:
            idx_split.append(idx)

    if len(idx_split) == 0:
        return [df]

    list_dfs = []
    for idx in idx_split:
        df_sample = df.loc[:idx-1, :].reset_index(drop=True)
        list_dfs.append(df_sample)
        df = df.loc[idx:, :]

    list_dfs.append(df.reset_index(drop=True))
    return list_dfs


def process_files(list_files):
    dfs = pandas.DataFrame()
    for file in list_files:
        df = read_csv(file)
        df = split_date_column(df)
        dfs = process_overlapping_dfs(df, dfs)
    list_dfs = split_date_dfs(dfs)
    return list_dfs


def save_dfs(list_dfs, key, path="./data/", product="WIN$N"):
    saved_files = []
    for df in list_dfs:
        date_start, date_end = get_start_end_dt(df)
        str_daterange = "_".join([date_start, date_end])
        filename = "_".join([path+product, key, str_daterange, ".csv"])
        df.to_csv(filename, index=False)
        saved_files.append(filename)
        print()
    return saved_files


def main():
    files = list_data_files()

    saved_files = []
    for key in files.keys():
        list_dfs = process_files(files[key])
        saved_files.append(save_dfs(list_dfs, key))
    return saved_files


if __name__ == '__main__':
    main()
