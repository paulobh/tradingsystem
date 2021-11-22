# from src import main
from src.helpers import main
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


def test_runstrat_main_FORCE():
    settings = json.load(open("./src/settings.json"))

    output = main.runstrat_main(settings, signal="EFISignal")
    assert output is None