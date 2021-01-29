# Trading Systems Simulator

## TO DO

-[ ] Test strategy for opening
-[ ] Increase rules with other indicators
-[ ] Improve documentation
-[ ] Fix source files path to data/source
-[ ] Set output files & reports to data/output

## Structure

```
tradingsystem/
    data/                   # store output and source files
        WDO$N_15M.csv
        WIN$N_10M.csv
        WIN$N_15M.csv
        WIN$N_1M.csv
        WIN$N_5M.csv
        samples/
            FB.csv
    docs/                   # used for web documentation
        __init__.py        
    src/                    # main source files
        args.py                 # auxiliy function, parse_args(), to parse args commands
        datafeed.py             # auxiliary function, pandasdatafeed(), to read source files
        main.py
        sample.py
        strategies.py
        __init__.py
    testes/                 # tests
        __init__.py
    .gitignore
    desktop.ini
    LICENSE.md
    README.md
    requirements.txt
```


## How to use

run on the terminal from the ``src`` directory:
``python main/py``

obs: if you get the message ``ImportError: cannot import name 'warnings' from 'matplotlib.dates' `` 
while running the program, remove the `warning` import on "backtrader/plot/locator.py"


## How to get source file

To generate the timeseries dataset is necessary to compile the script "coletar_mini_xp.mql5" on Metatrader in order to generate the ".ex5" file and then run it.

To access the MetaQuotes, the script editor in Metatrader, press F4 on the main window

In order to change the security collected you need to change the variable `nome_ativo`, for example:
``
string nome_ativo= "WIN$N"
``


## Args

The `args.py` file is responsible to store the default arguments use on main file `main.py`.
Along the parameters there is the ones relates with:
 - Data Feed
    - `--data`  Specific data to be loaded
    - `--fromdate`  Starting date in YYYY-MM-DD format
    - `--todate`  Ending date in YYYY-MM-DD format
    - `--noheaders`  If on the source data file, should not use header rows
    - `--noprint`  Print the dataframe
 - Strategy
    - `--cash`  Cash to start with
    - `--exitsignal`  Signal type to use for the exit signal
    - `--exitperiod`  Period for the exit control ATR
 - Cerebro
    - `--cerebro`  kwargs in key=value format
    - `--broker`  kwargs in key=value format
    - `--sizer`  kwargs in key=value format
    - `--strat`  kwargs in key=value format
 - Plot
    - `--plot`  Plot the read data applying any kwargs passed
        - `--plot style="candle"` to plot candles

## Setup enviroment

Using bash:
```
python3 -m pip install --upgrade pip
pip3 install virtualenv
pip3 install --upgrade setuptools

virtualenv -p ./venv venv
python -m venv venv

deactivate
conda deactivate

source ./venv/Scripts/activate
./venv/Scripts/activate
```

```
where python
which python3
python --version
python -V
```

### Useful Commands
```
rm -r venv # remove directory

#create alias on bash
cd
echo alias ll=\'ls -l\' >> .bashrc
echo alias act=\'source ./venv/Scripts/activate\' >> .bashrc

```

#References

[Backtrader](https://www.backtrader.com/)

[Backtrader Github](https://github.com/mementum/backtrader)

[Metatrader Docs.](https://www.mql5.com/pt/docs)