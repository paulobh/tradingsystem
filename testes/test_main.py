# from src import main
from src import main_opt
import json
# from src.args import parse_args


settings = json.load(open(f"./src/settings.json"))


# def test_analyzers_log():
#     # input_result =
#     output = main.analyzers_log()
#     assert False
#
# def test_analyzers_read():
#     main.analyzers_read()
#     assert False
#
# def test_runstrat_opt():
#     output = main.runstrat_opt()
#     assert output is None
#
# def test_main_opt():
#     output = main.main_opt()
#     assert output is None

def test_daterange_opt():
    params_signal = {"RSISignal": {
      "period_rsi": [10, 30, 10],
      "threshold_buy": [10, 30, 10],
      "threshold_sell": [70, 90, 10]
    }}
    output = main_opt.daterange_opt(settings, params_signal)
    assert output is None