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

tabels to do:
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
import json
import pandas

from time import process_time


def train_signal_analyzers(settings):
    settings = json.load(open("./src/settings.json"))
    filename = settings["opt_analyzer"]["path_opt_parms"]

    with open(filename, "r") as file:
        data = json.load(file)
        df_data = pandas.DataFrame()

        for idx, row in enumerate(data):
            dt_train = {"dt_train": row.pop("train")}
            dt_test = {"dt_test": row.pop("test")}

            df_row = pandas.DataFrame()
            df_row.insert(0, "dt_train", tuple(dt_train.values()))
            df_row.insert(1, "dt_test", tuple(dt_test.values()))

            for key, value in row.items():
                for signal, params in value.items():
                    data_signal_analyzer = params["analyzer_opt"]
                    entries_to_remove = ["analyzer_opt"]
                    [params.pop(k) for k in entries_to_remove]

                    params["time_start"] = tuple(params.get("time_start", [9, 0]))
                    params["time_stop"] = tuple(params.get("time_stop", [17, 0]))
                    pandas.concat([df_row, tuple(params)], ignore_index=True, keys=".".join([signal, "params"]))
                    # {".".join([signal, "params"]): tuple(params)}])
                    df_row.append({".".join([signal, "params"]): tuple(params)})


                    df_params = pandas.DataFrame.from_dict(params, orient="index").T

                    df_params_analyzers = pandas.DataFrame.from_dict(data_signal_analyzer, orient="index")
                    df_params_analyzers = df_params_analyzers.T.add_prefix("analyzers.")

                    df_signal = pandas.concat([df_params, df_params_analyzers], axis=1)
                    df_signal = df_signal.add_prefix(signal+".")
                    df_row = pandas.concat([df_row, df_signal], axis=1)


            df_sample = pandas.DataFrame(row)
            df_data.append(df_sample)

    return df_data


def convert_dict_values_to_tuple(dictionary):
    return {{key: tuple(value)} for key, value in dictionary.items()}


def main(settings):
    df_train = train_signal_analyzers(settings)

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