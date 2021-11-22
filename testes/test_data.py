import os
import pandas

from data.analysis import data

os.chdir('..')


def test_list_data_files():
    output = data.list_data_files()
    assert isinstance(output, dict)
    assert len(output) > 0


def test_read_csv():
    expected_input = "./data/WIN$N_1M_2021.01.20_2020.04.24.csv"
    output = data.read_csv(expected_input)
    assert isinstance(output, pandas.DataFrame)
    assert len(output) > 0


def test_split_date_column():
    expected_filename = "./data/WIN$N_1M_2021.01.20_2020.04.24.csv"
    expected_input = data.read_csv(expected_filename)
    output = data.split_date_column(expected_input)
    assert isinstance(output, pandas.DataFrame)
    assert len(output) > 0
    assert "hour" in list(output.columns)


def test_get_start_end_dt():
    expected_filename = "data/WIN$N_1M_2015.12.30_2015.08.12.csv"
    expected_df = data.read_csv(expected_filename)
    expected_df = data.split_date_column(expected_df)
    output = data.get_start_end_dt(expected_df)
    assert output == ('2015.08.12', '2015.12.30')


def test_process_overlapping_dfs():
    expected_filename = "./data/WIN$N_1M_2021.01.20_2020.04.24.csv"
    expected_df1 = data.read_csv(expected_filename)
    expected_df1 = data.split_date_column(expected_df1)

    expected_filename = "./data/WIN$N_1M_2020.08.21_2019.11.21.csv"
    expected_df2 = data.read_csv(expected_filename)
    expected_df2 = data.split_date_column(expected_df2)

    output = data.process_overlapping_dfs(expected_df1, expected_df2)
    assert isinstance(output, pandas.DataFrame)

    output_dates = data.get_start_end_dt(output)
    assert output_dates == ('2019.11.21', '2021.01.20')


def test_split_dates_dfs():
    expected_filenames = [
        "data/WIN$N_1M_2015.12.30_2015.08.12.csv",
        "./data/WIN$N_1M_2020.08.21_2019.11.21.csv"]
    expected_input_df = data.process_files(expected_filenames)
    output = data.split_date_dfs(expected_input_df)
    assert isinstance(output, list)
    assert isinstance(output[0], pandas.DataFrame)
    assert len(output) == 2

    output_dates = data.get_start_end_dt(output[0])
    assert output_dates == ('2015.08.12', '2015.12.30')
    output_dates = data.get_start_end_dt(output[1])
    assert output_dates == ('2019.11.21', '2020.08.21')


    expected_filenames = [
        "data/WIN$N_1M_2015.12.30_2015.08.12.csv"]
    expected_input_df = data.process_files(expected_filenames)
    output = data.split_date_dfs(expected_input_df)
    assert isinstance(output, list)
    assert isinstance(output[0], pandas.DataFrame)
    assert len(output) == 1

    output_dates = data.get_start_end_dt(output[0])
    assert output_dates == ('2015.08.12', '2015.12.30')


def test_process_files():
    # expected_filenames = [
    #     "data/helpers/WIN$N_1M_2015.12.30_2015.08.12.csv",
    #     "./data/helpers/WIN$N_1M_2020.08.21_2019.11.21.csv"]
    # output = data.process_files(expected_filenames)
    # assert isinstance(output, list)
    # assert isinstance(output[0], pandas.DataFrame)
    # assert len(output) == 2

    # expected_filenames = [
    #     "./data/WIN$N_1M_2015.12.30_2015.08.12.csv",
    #     "./data/WIN$N_1M_2020.08.21_2019.11.21.csv",
    #     "./data/WIN$N_1M_2021.01.20_2020.04.24.csv"]
    # output = data.process_files(expected_filenames)
    # assert isinstance(output, list)
    # assert isinstance(output[0], pandas.DataFrame)
    # assert len(output) == 2

    expected_filenames = [
        "./data/helpers/WIN$N_10M_2020.08.21_2015.08.12.csv",
        "./data/helpers/WIN$N_10M_2021.01.22_2015.12.16.csv"]
    output = data.process_files(expected_filenames)
    assert isinstance(output, list)
    assert isinstance(output[0], pandas.DataFrame)
    assert len(output) == 1


# @patch.object(pandas.DataFrame, "to_csv")
# def test_save_dfs(mock_to_csv):
def test_save_dfs():
    expected_filenames = [
        "./data/WIN$N_1M_2015.12.30_2015.08.12.csv",
        "./data/WIN$N_1M_2020.08.21_2019.11.21.csv",
        "./data/WIN$N_1M_2021.01.20_2020.04.24.csv"]
    expected_input_dfs = data.process_files(expected_filenames)
    output = data.save_dfs(expected_input_dfs, key="1M")
    assert isinstance(output, list)
    assert len(output) == 2
    # assert mock_to_csv.called
