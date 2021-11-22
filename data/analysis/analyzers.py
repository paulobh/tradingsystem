""" Data analysis functions for output files
associated with : ``

plots to do:
- training data; vwr para cada sinal ao longo do tempo
    objetivo: observar performance historica do sinal com os seus parametros otimos
    se comparado com outros indicadores podemos inferir algumas coisas:
        se todos apresentarem compostamentos semelhantes em algum momento
        se todos apresentarem compostamentos diverntes em algum momento
        se algum indicador for constantemente negativo/positivo
        se algum indicador for constantemente volatil

- test data; linha para cada sinal usado e seus vwr do treino, assim como o agregado
    objetivo: observaser performance do agregado e como diverge dos otimos de cada sinal usado no treino.
    se comparado com outros indicadores podemos inferir algumas coisas:
        se agregado for constantemente negativo/positivo
        se agregado for constantemente volatil
        se o agregado diverge muito entre o maximo e minimo dos sinais no treino

tabelas to do:
- settings; parametros usados para signals
- date_train | date_test | col_signal1 | col_signal2 | col_signalMAX | col_signalMIN |col_signalAVG |
                           vwr_train / days_train | vwr_test / days_train (para cada sinal)
    comparar retornos no treino e test
- date_train | col_signal1 | col_signal2 | ... | vwr
    comparar os retorno/pesos de cada indicador ao longo do tempo
- date_train | col_signal | col_param1 | col_param2 | ... | vwr     (for each signal)
    comparar oscilação dos parametros otimos ao longo do tempo, util para definir ranges dos parametros


- obs:
    * seria interessante rodar o otimizador para os dados de test e ver como eles se comportaria nesse periodo?
    * seria interessante usar uma janela deslizante , para gerar mais dados de treino/teste ?


"""
import sys
import json
import pandas
import numpy as np
import datetime as dt
import matplotlib.pyplot as plt
import seaborn as sns
import warnings

from time import process_time
from pandas.core.common import SettingWithCopyWarning

warnings.simplefilter(action="ignore", category=SettingWithCopyWarning)
sns.set_theme(style="whitegrid")


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


def df_extract_values(settings):
    opt_type = "test"
    filename, output_key = filename_key_opt_type(settings, opt_type=opt_type)

    with open(filename, "r") as file:
        data = json.load(file)
        df_data = pandas.DataFrame(data)
        file.close()

    # split output_type: [test, train]
    cols_ids = ["train", "test"]
    df_data = df_data.melt(id_vars=cols_ids, var_name="output_type")

    # split signals
    cols_ids = ["train", "test", "output_type"]
    df_data = df_split_param(df_data, cols_ids, var_name="signal")

    # split params
    cols_ids = ["train", "test", "output_type", "signal"]
    df_data = df_split_param(df_data, cols_ids, var_name="params")

    # # fix time_stop/start, list
    df_data = df_time_fix(df_data)

    # split analyzer_opt
    df_data = df_split_params_opt(df_data)

    # finals adjustments
    df_data = df_data.reset_index(drop=True)
    df_data["signal"] = [x.split("Signal")[0] if len(x) > 7 else x for x in df_data["signal"]]
    df_data["output_type"] = [x.split("_")[1] for x in df_data["output_type"]]
    df_data = df_data.rename(columns={"output_type": "type"})

    return df_data


def df_split_params_opt(df):
    filter_params = df["params"] == "analyzer_opt"
    df_analyzers = df[filter_params]
    df_params = df[~filter_params]

    # update params col
    cols_ids = ["train", "test", "output_type", "signal", "value"]
    df_params = df_params.melt(id_vars=cols_ids, var_name="var_type", value_name="variable")

    # update analyzers col
    df_analyzers = df_analyzers.rename(columns={"params": "var_type"})
    cols_ids = ["train", "test", "output_type", "signal", "var_type"]
    df_analyzers = df_split_param(df_analyzers, cols_ids, var_name="variable")

    # update analyzers col from Signals
    filter_signals = df_analyzers["signal"].isin(["Signals","BuyHold"])
    # filter_signals = df_analyzers["signal"] == "Signals"
    df_analyzers_signals = df_analyzers[filter_signals]
    df_analyzers = df_analyzers[~filter_signals]

    # update analyzers col from Signals with dict on values
    cols_ids = ["train", "test", "output_type", "signal", "var_type", "variable"]
    df_analyzers_signals = df_split_param(df_analyzers_signals, cols_ids, var_name="var")
    df_analyzers_sig_new = df_split_params_opt_Signals(df_analyzers_signals)

    # concat all sub tables, split before
    df_analyzers_sig_new = df_analyzers_sig_new.rename(columns={"var": "variable"})
    df_analyzers = pandas.concat([df_analyzers, df_analyzers_sig_new])

    df_opt = pandas.concat([df_params, df_analyzers])
    return df_opt


def df_split_params_opt_Signals(df_analyzers_signals):
    output_dict = {
        "VWR": ["vwr"],
        "SQN": ["sqn"],
        "TradeAnalyzer": ["pnl", "net"]
        # "TradeAnalyzer": {"pnl": "net"}
    }

    df_analyzers_sig_new = pandas.DataFrame()
    for opt in output_dict.keys():
        filter_opt = df_analyzers_signals["variable"] == opt
        df_analyzers_sample = df_analyzers_signals[filter_opt].drop(columns="variable")
        filter_var = df_analyzers_sample["var"].isin(output_dict[opt])
        df_analyzers_sample = df_analyzers_sample[filter_var]

        if opt == "TradeAnalyzer":
            # filter_var = df_analyzers_sample["var"] == list(output_dict[opt].keys())[0]
            filter_var = df_analyzers_sample["var"] == output_dict[opt][0]
            cols_ids = ["train", "test", "output_type", "signal", "var_type", "var"]
            df_analyzers_sample = df_split_param(df_analyzers_sample[filter_var],
                                                  cols_ids, var_name="var1")

            # filter_var = df_analyzers_sample["var1"] == list(output_dict[opt].values())[0]
            filter_var = df_analyzers_sample["var1"] == output_dict[opt][1]
            cols_ids = ["train", "test", "output_type", "signal", "var_type", "var", "var1"]
            df_analyzers_sample = df_split_param(df_analyzers_sample[filter_var],
                                                 cols_ids, var_name="var2")

            filter_var = df_analyzers_sample["var2"] == "total"
            df_analyzers_sample = df_analyzers_sample[filter_var]
            cols_drop = ["var", "var1"]
            df_analyzers_sample = df_analyzers_sample.drop(columns=cols_drop)
            df_analyzers_sample = df_analyzers_sample.rename(columns={"var2": "var"})

        df_analyzers_sig_new = pandas.concat([df_analyzers_sig_new, df_analyzers_sample])

    return df_analyzers_sig_new


def df_split_param(df, cols_ids, var_name):
    df_values = df["value"].apply(pandas.Series)
    df_melt = df.drop(["value"], axis=1)
    df_split = pandas.concat([df_melt, df_values], axis=1)
    df_split = df_split.melt(id_vars=cols_ids, var_name=var_name)
    df_split = df_split.dropna()
    return df_split


def df_time_fix(df):
    # fix time_stop/start, list
    varaibles_time = ["time_start", "time_stop"]
    filter_var = df["params"].isin(varaibles_time)
    df.loc[filter_var, "value"] = df.loc[filter_var, "value"].apply(
        lambda x: x[0] + x[1] / 60)
    return df


# def df_analyzers(settings, train_test="train"):
#     opt_type_dict = {
#         "train": {"key": "output_train_key", "path": "path_output_train"},
#         "test": {"key": "output_test_key", "path": "path_output_test"}
#     }
#     opt_type = train_test
#     output_key = settings["opt_analyzer"][opt_type_dict[opt_type]["key"]]
#     output_key_train = settings["opt_analyzer"][opt_type_dict["train"]["key"]]
#
#     days_train = settings["opt_analyzer"]["daterange_opt"]
#     range_train = settings["opt_analyzer"]["daterange_opt_train"]
#     filename = settings["opt_analyzer"][opt_type_dict[opt_type]["path"]].format(days_train, range_train)
#
#     with open(filename, "r") as file:
#         data = json.load(file)
#         df_data = pandas.DataFrame()
#         for idx, row in enumerate(data):
#             df_row = df_row_dates(row)
#             df_row = df_row_output_key(df_row, row, output_key=output_key_train)
#             if train_test == "test":
#                 df_row = df_row_output_key(df_row, row, output_key=output_key)
#             df_data = pandas.concat([df_data, df_row])
#
#     df_data = df_data.reset_index(drop=True)
#     return df_data
#
# # def df_analyzers_train_test(settings, train_test="train"):
# #     settings_train_test = {
# #         "train": "path_opt_parms",
# #         "test": "path_output"
# #     }
# #     filename = settings["opt_analyzer"][settings_train_test[train_test]]
# #     with open(filename, "r") as file:
# #         data = json.load(file)
# #         df_data = pandas.DataFrame()
# #         for idx, row in enumerate(data):
# #             df_data = df_row_signal(df_data, row, "signal")
# #             if train_test == "test":
# #                 df_data = df_row_analyzers(df_data, row, "analyzers")
# #     return df_data
#
# # def df_row_signal(df_data, row_dict, output_key='output_train'):
# # # def df_row_signal(df_data, row_dict, output_key="signal"):
# #     dt_train = {"dt_train": row_dict.pop("train")}
# #     dt_test = {"dt_test": row_dict.pop("test")}
# #
# #     df_row = pandas.DataFrame()
# #     df_row.insert(0, "dt_train", tuple(dt_train.values()))
# #     df_row.insert(1, "dt_test", tuple(dt_test.values()))
# #
# #     row = row_dict[output_key]
# #     for signal, params in row.items():
# #         params["time_start"] = tuple(params.get("time_start", [9, 0]))
# #         params["time_stop"] = tuple(params.get("time_stop", [17, 0]))
# #         df_row = df_concat_row(df_row, params, signal, "params")
# #
# #         data_signal_analyzer = params.pop("analyzer_opt")
# #         df_row = df_concat_row(df_row, data_signal_analyzer, signal, "analyzers")
# #
# #     df_data = pandas.concat([df_data, df_row])
# #     df_data = df_data.reset_index(drop=True)
# #     return df_data
#
#
# # def df_row_analyzers(df_data, row_dict, output_key="analyzers"):
# #     row = row_dict[output_key]
# #     output_col = ".".join(["Output", output_key])
# #     df_row = df_data.tail(1).copy()
# #     df_row = df_row.drop(output_col, errors='ignore', axis=1)
# #     df_row = df_row.reset_index(drop=True)
# #     df_data = df_data.drop(df_data.tail(1).index)
# #
# #     df_row_output = df_concat_row(df_row, row, "Output", output_key)
# #     df_data = pandas.concat([df_data, df_row_output])
# #     df_data = df_data.reset_index(drop=True)
# #     return df_data
#
# # def df_plot_train_signals_objetive(settings, df, f_objetive=None):
# #     if f_objetive is None:
# #         f_objetive = settings["opt_analyzer"]["analyzer_opt"]
# #     cols_analyzer = [col for col in df.columns if "analyzers" in col]
# #     df_analyzers = df[cols_analyzer]
# #
# #     output_dict = {
# #         "vwr": {"VWR": "vwr"},
# #         "sqn": {"SQN": "sqn"},
# #         "tradeanalyzer": {"TradeAnalyzer": {"pnl": "net"}}
# #     }
# #
# #     for col in df_analyzers:
# #         if "Output" in col:
# #             f_obj1 = list(output_dict[f_objetive].keys())[0]
# #             f_obj1_1 = list(output_dict[f_objetive].values())[0]
# #             f_obj_values = [row[f_obj1][f_obj1_1] for row in df_analyzers[col]]
# #         else:
# #             f_obj_values = [row[f_objetive] for row in df_analyzers[col]]
# #         df_analyzers[col] = f_obj_values
# #     return df_analyzers
#
# def df_concat_row(df_row, params_dict, name, subname):
#     params_name = ".".join([name, subname])
#     params = {params_name: params_dict}
#     params_series = pandas.Series(tuple(params.values()), name=params_name)
#     df_row = pandas.concat([df_row, params_series], axis=1)
#     return df_row
#
#
# def df_row_dates(row_dict):
#     dt_train = {"dt_train": row_dict.pop("train")}
#     dt_test = {"dt_test": row_dict.pop("test")}
#     df_row = pandas.DataFrame()
#     df_row.insert(0, "dt_train", tuple(dt_train.values()))
#     df_row.insert(1, "dt_test", tuple(dt_test.values()))
#     return df_row
#
#
# def df_row_params_time(params):
# # def df_row_params_time(df_row, params, signal):
#     if "time_start" in params.keys():
#         params["time_start"] = tuple(params.get("time_start", [9, 0]))
#     if "time_stop" in params.keys():
#         params["time_stop"] = tuple(params.get("time_stop", [17, 0]))
#     # df_row = df_concat_row(df_row, params, signal, "params")
#     return params
#
#
# def df_row_output_key(df_row, row_dict, output_key='output_train'):
#     for signal, params in row_dict[output_key].items():
#         params = df_row_params_time(params)
#         data_signal_analyzer = params.pop("analyzer_opt")
#         output_signal = ".".join([output_key, signal])
#         df_row = df_concat_row(df_row, params, output_signal, "params")
#         df_row = df_concat_row(df_row, data_signal_analyzer, output_signal, "analyzers")
#     return df_row


def table_plot_signal_opt(df):
    signals = set(df["signal"])
    signals.discard("Signals")
    for signal in signals:
        filter_signal = df["signal"] == signal
        filter_type = df["var_type"] == "params"
        df_signal = df[filter_signal & filter_type]

        varaibles_time = ["time_start", "time_stop"]
        filter_var = df_signal["variable"].isin(varaibles_time)
        df_signal = df_signal[~filter_var]

        ax = sns.boxplot(data=df_signal, x="output_type", y="value", hue="variable")
        # ax = sns.swarmplot(data=df_signal, x="output_type", y="value", hue="variable")
        ax.set_title(signal)
        plt.show()
    return


def plot_signal(df):
    plt.figure()
    # df.plot.hist(alpha=0.5)
    # df.plot.hist(stacked=True)
    df.plot()
    plt.show()
    return


def plot_boxplot(df):
    plt.figure()
    # df.plot.hist(alpha=0.5)
    # df.plot.hist(stacked=True)
    df.boxplot()
    plt.show()
    return


def plot_cumsum(df):
    plt.figure()
    df.cumsum().plot()
    plt.show()
    return


# def table_params(df, f_objetive=None):
#     cols_dates = ["dt_train", "dt_test"]
#     df_melt = df.melt(id_vars=cols_dates, var_name="signal")
#     # df_melt = df_melt.rename(columns={"variable": "signal"})
#     cols_dates.append("signal")
#
#     df_values = df_melt["value"].apply(pandas.Series)
#     df_melt = df_melt.drop(["value"], axis=1)
#     df_params = pandas.concat([df_melt, df_values], axis=1)
#
#     df_params_melt = df_params.melt(id_vars=cols_dates).dropna()
#     df_params_melt[["output_type", "signal", "var_type"]] = df_params_melt["signal"].str.split(".", expand=True)
#
#     varaibles_time = ["time_start", "time_stop"]
#     filter_var = df_params_melt["variable"].isin(varaibles_time)
#     df_params_melt.loc[filter_var, "value"] = df_params_melt.loc[filter_var, "value"].apply(
#         lambda x: x[0] + x[1] / 60)
#
#     return df_params_melt


def table_params_output(df):
    def rename(newname):
        def decorator(f):
            f.__name__ = newname
            return f

        return decorator

    def q_at(y):
        @rename(f'q{y:0.2f}')
        def q(x):
            return x.quantile(y)

        return q

    # cols_filter = ["output_type", "signal", "var_type", "variable", "value"]
    cols_filter = ["signal", "var_type", "variable", "value"]
    df = df.loc[:, cols_filter]

    agg_dict = {
        "value": ["min", "max", q_at(0.25), q_at(0.5), q_at(0.75)]  # lambda x: x.quantile(0.25)
    }
    # groupby_index = ["signal", "variable", "output_type"]
    groupby_index = ["signal", "variable"]
    filter_type = df["var_type"] == "params"
    df_new = df[filter_type].groupby(groupby_index).agg(agg_dict)
    df_new.columns = df_new.columns.droplevel()
    df_new = df_new.reset_index()
    df_new["signal"] = [x.split("Signal")[0] for x in df_new["signal"]]

    out_markdown = df_new.to_markdown(index=False)
    return df_new, out_markdown


def table_output_type(df, cols_indx, type):
    def rename(newname):
        def decorator(f):
            f.__name__ = newname
            return f

        return decorator

    def q_at(y):
        @rename(f'q{y:0.2f}')
        def q(x):
            return round(x.quantile(y), 2)

        return q

    agg_dict = {
        "value": ["min", "max", q_at(0.25), q_at(0.5), q_at(0.75)]  # lambda x: x.quantile(0.25)
    }
    # groupby_index = ["signal", "output_type", "variable"]
    filter_type = df["var_type"] == type

    df_new = df[filter_type].groupby(by=cols_indx).agg(agg_dict)
    df_new.columns = df_new.columns.droplevel()
    df_new = df_new.reset_index()


    out_latex = df_new.to_latex(index=False)
    return df_new, out_latex


def table_diff(df, col_diff=["type"], col_value="value"):
    cols_indx = df.columns.drop(col_diff)
    cols_indx = cols_indx.drop(col_value)
    cols_indx = cols_indx.drop(["train","test"])
    cols_indx = list(cols_indx)

    agg_dict = {
        col_value: "diff"
    }
    df_new = df.groupby(cols_indx).agg(agg_dict).dropna()
    df_new[col_diff] = "diff"

    cols_indx = df.columns.drop(col_diff)
    cols_indx = cols_indx.drop(col_value)
    df_index = df.loc[df_new.index, cols_indx]
    df_new = pandas.concat([df_index,df_new], axis=1)
    df = pandas.concat([df,df_new])

    return df


# def plot_objetive_signals_boxplot(settings, df, f_objetive=None):
#     if f_objetive is None:
#         f_objetive = settings["opt_analyzer"]["analyzer_opt"]
#
#     filter_var_type = df["var_type"] == "analyzer_opt"
#     filter_objective = df["variable"] == f_objetive
#     df = df[filter_var_type & filter_objective]
#
#     df_melt = df["train"].apply(pandas.Series)
#     df = pandas.concat([df_melt, df], axis=1)
#     df = df.sort_values(by=["fromdate", "type", "var_type", "signal", "variable"])
#     df["value"] = df["value"].astype("float")
#
#     ax = sns.catplot(data=df, x="signal", y="value", col="type", kind="box")
#     ax.fig.suptitle(f_objetive.upper())
#     plt.show()
#     return df


def plot_objetive_signals_box(settings, df, f_objetive="vwr", diff=False):
    filename = sys._getframe().f_code.co_name
    if f_objetive is None:
        f_objetive = settings["opt_analyzer"]["analyzer_opt"]
    filename = "_".join([filename,f_objetive])

    filter_var_type = df["var_type"] == "analyzer_opt"
    filter_objective = df["variable"] == f_objetive
    df = df[filter_var_type & filter_objective]

    df_melt = df["train"].apply(pandas.Series)
    df = pandas.concat([df_melt, df], axis=1)
    df = df.sort_values(by=["fromdate", "type", "var_type", "signal", "variable"])
    df["value"] = df["value"].astype("float")
    df["fromdate"] = [dt.datetime.strptime(d, '%Y-%m-%d %H:%M:%S').date() for d in df["fromdate"]]

    if diff:
        df = table_diff(df, col_diff=["type"], col_value="value")
        filename = "_".join([filename, "diff"])

    ax = sns.catplot(data=df, x="signal", y="value", col="type", kind="box")
    ax.fig.suptitle(f_objetive.upper(), y=1)
    plt.show()

    filename = "_".join([filename, ".png"])
    filename = "".join(["./docs/output/", filename])
    ax.savefig(filename, transparent=True)
    return df


def plot_objetive_dates_line(settings, df, f_objetive=None, diff=False):
    filename = sys._getframe().f_code.co_name
    if f_objetive is None:
        f_objetive = settings["opt_analyzer"]["analyzer_opt"]
    filename = "_".join([filename, f_objetive])

    filter_var_type = df["var_type"] == "analyzer_opt"
    filter_objective = df["variable"] == f_objetive
    df = df[filter_var_type & filter_objective]

    df_melt = df["train"].apply(pandas.Series)
    df = pandas.concat([df_melt, df], axis=1)
    df = df.sort_values(by=["fromdate", "type", "var_type", "signal", "variable"])
    df["value"] = df["value"].astype("float")
    df["fromdate"] = [dt.datetime.strptime(d, '%Y-%m-%d %H:%M:%S').date() for d in df["fromdate"]]

    if diff:
        df = table_diff(df, col_diff=["type"], col_value="value")
        filename = "_".join([filename, "diff"])

    ax = sns.relplot(data=df, x="fromdate", y="value", col="type",
                     hue="signal", style="signal", kind="line")
    ax.fig.suptitle(f_objetive.upper(), y=1)
    plt.show()

    filename = "_".join([filename, ".png"])
    filename = "".join(["./docs/output/", filename])
    ax.savefig(filename, transparent=True)
    return df


def plot_param_signals_box(df, signal, diff=False, stops=False):
    filename = sys._getframe().f_code.co_name
    filename = "_".join([filename, signal])

    filter_var_type = df["var_type"] == "params"
    filter_signal = df["signal"] == signal
    if stops:
        filename = "_".join([filename, "stops"])
        filter_param = df["variable"].isin(["atrdist", "atrprofit"])
        df = df[filter_var_type & filter_signal & filter_param]
    else:
        filter_param = df["variable"].isin(["time_start", "time_stop", "atrdist", "atrprofit"])
        df = df[filter_var_type & filter_signal & ~filter_param]

    df_melt = df["train"].apply(pandas.Series)
    df = pandas.concat([df_melt, df], axis=1)
    df = df.sort_values(by=["fromdate", "type", "var_type", "signal", "variable"])
    df["value"] = df["value"].astype("float")
    df["fromdate"] = [dt.datetime.strptime(d, '%Y-%m-%d %H:%M:%S').date() for d in df["fromdate"]]

    if diff:
        df = table_diff(df, col_diff=["type"], col_value="value")
        filename = "_".join([filename, "diff"])

    ax = sns.catplot(data=df, x="variable", y="value", col="type", kind="box")
    ax.fig.suptitle(signal.upper(), y=1)
    plt.show()

    filename = "_".join([filename, ".png"])
    filename = "".join(["./docs/output/", filename])
    ax.savefig(filename, transparent=True)
    return df


def plot_params_dates_line(df, signal, diff=False, stops=False):
    filename = sys._getframe().f_code.co_name
    filename = "_".join([filename, signal])

    filter_var_type = df["var_type"] == "params"
    filter_signal = df["signal"] == signal
    if stops:
        filename = "_".join([filename, "stops"])
        filter_param = df["variable"].isin(["atrdist", "atrprofit"])
        df = df[filter_var_type & filter_signal & filter_param]
    else:
        filter_param = df["variable"].isin(["time_start", "time_stop", "atrdist", "atrprofit"])
        df = df[filter_var_type & filter_signal & ~filter_param]

    df_melt = df["train"].apply(pandas.Series)
    df = pandas.concat([df_melt, df], axis=1)
    df = df.sort_values(by=["fromdate", "type", "var_type", "signal", "variable"])
    df["value"] = df["value"].astype("float")
    df["fromdate"] = [dt.datetime.strptime(d, '%Y-%m-%d %H:%M:%S').date() for d in df["fromdate"]]

    if diff:
        df = table_diff(df, col_diff=["type"], col_value="value")
        filename = "_".join([filename, "diff"])

    ax = sns.relplot(data=df, x="fromdate", y="value", col="type",
                     hue="variable", style="variable", kind="line")
    ax.fig.suptitle(signal.upper(), y=1)
    plt.show()

    filename = "_".join([filename, ".png"])
    filename = "".join(["./docs/output/", filename])
    ax.savefig(filename, transparent=True)
    return df


def main(settings):
    # df_train = df_analyzers_train_test(settings, train_test="train")
    # df_test = df_analyzers_train_test(settings, train_test="test")
    # df_analyzers_train = df_plot_train_signals_objetive(settings, df=df_train, f_objetive="vwr")
    # df_analyzers_test = df_plot_train_signals_objetive(settings, df=df_test, f_objetive="vwr")
    # plot_signal(df_analyzers_train)
    # plot_cumsum(df_analyzers_train)

    # df_train = df_analyzers(settings, train_test="train")
    # df_test = df_analyzers(settings, train_test="test")
    # df_analyzers_test = df_plot_objetive(settings, df=df_test, f_objetive="vwr")
    # df_analyzers_test = df_plot_objetive(settings, df=df_test, f_objetive="tradeanalyzer")
    # df_values = table_params(df_test, f_objetive=None)
    # table_plot_signal_opt(df_params)
    # plot_signal(df_analyzers_test)
    # plot_boxplot(df_analyzers_test)
    # plot_cumsum(df_analyzers_test)
    # df_params_table, params_markdown = table_params_output(df_values)
    # df_analyzers_table, analyzers_markdown = table_output_type(df_values)

    df_values = df_extract_values(settings)


    # # Generate tables: 1
    # cols_idx = ["signal", "variable"]
    # df_params_table, params_latex = table_output_type(df_values, cols_idx, "params")
    #
    # # Generate tables: 2
    # cols_idx = ["signal", "variable", "type"]
    # df_analyzers_table, analyzers_latex = table_output_type(df_values, cols_idx, "analyzer_opt")

    # # Generate plots: 1
    # plot_objetive_signals_box(settings, df_values, f_objetive="vwr")
    #
    # Generate plots: 2
    plot_objetive_signals_box(settings, df_values, f_objetive="vwr", diff=True)
    #
    # # Generate plots: 3
    # plot_objetive_dates_line(settings, df_values, f_objetive="vwr")
    #
    # Generate plots: 4
    plot_objetive_dates_line(settings, df_values, f_objetive="vwr", diff=True)
    #
    # # Generate plots: 5
    # signals = list(df_values["signal"].unique())
    # signals.remove("Signals")
    # [plot_param_signals_box(df_values, signal=signal) for signal in signals]
    #
    # # Generate plots: 6
    # signals = list(df_values["signal"].unique())
    # signals.remove("Signals")
    # [plot_param_signals_box(df_values, signal=signal, diff=True) for signal in signals]
    #
    # # Generate plots: 7
    # signals = list(df_values["signal"].unique())
    # signals.remove("Signals")
    # [plot_params_dates_line(df_values, signal=signal, diff=False) for signal in signals]
    #
    # # Generate plots: 8
    # signals = list(df_values["signal"].unique())
    # signals.remove("Signals")
    # [plot_params_dates_line(df_values, signal=signal, diff=True) for signal in signals]
    #
    # # Generate plots: 9
    # signals = list(df_values["signal"].unique())
    # signals.remove("Signals")
    # signals.remove("ElderForceIndex")
    # [plot_params_dates_line(df_values, signal=signal, diff=True, stops=True) for signal in signals]
    #
    # # Generate plots: 10
    # signals = list(df_values["signal"].unique())
    # signals.remove("Signals")
    # signals.remove("ElderForceIndex")
    # [plot_param_signals_box(df_values, signal=signal, diff=True, stops=True) for signal in signals]

    return None


if __name__ == '__main__':
    settings = json.load(open("./src/settings.json"))

    # clock the start of the process
    tstart = process_time()

    # main script
    main(settings)

    # clock the end of the process
    tend = process_time()

    # print out the result
    print('Total Time used:', str(tend - tstart))