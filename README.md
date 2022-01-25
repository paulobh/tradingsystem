# Trading Systems Simulator

Investment automation is a challenge since the beginning of stock markets. 
With the evolution of computational power, this dream is getting closer to reality.

In this context, this repository develops and apply some computational techniques to automate investments.
The proposed tool for backtesting multicriteria decision making investment strategies signal based, has some simple outputs such as buy, wait and sell.
This approach is made in a way that removes some psychological aspects of human’s traders, that have significant impact on the decision making process under uncertainty conditions. 

Similar to others approaches it uses technical indicators, however it is different from usual approaches, this method focuses on usage for day trade operation of mini future contracts of index Bovespa, with candles of $5$ minutes frequency.
Even though, the proposed tool seems to be relevant 
(i) to improve  the data acquisition process, that can be challenging  depending of the equity and frequency; 
(ii) for data analysis, with customs metrics and visualizations; 
(iii) and for optimization and validation of custom and complex strategies, using python, that could be more challenging to implement using MQL5 on metatrader.

This project used [backtrader](https://www.backtrader.com/), that is a python framework, used to backtesting and trading, allowing you to focus on writing reusable trading strategies, indicators and analyzers instead of spending time building infrastructure.
This framework is great for custom-made strategies, with a [open source](https://github.com/mementum/backtrader) code, and plenty of [documentation](https://www.backtrader.com/docu/) and some quick [examples](https://www.backtrader.com/home/helloalgotrading/). 
When all that is not enough, you can enjoy the [community](https://community.backtrader.com/), extremely relevant from my point of view.

## Structure

```
tradingsystem/
    data/                   # store output and source files
        analysis/           # source files used to analise data
            analyzers.py
            data.py         # source file used to structure, clean and orgnize source time series data
            data_analysis.ipynb #file used for data analysis
            data_analysis.py    #source file with functions used on data_analysis.py
        analyzers_opt/      # store output of optimization steps
        samples/            # source files used to extract data from metatrader
            coletar_mini_xp_dates - Shortcut.lnk
            samples.rar     #mql5 files necessary to downlaod data from metatrader
    docs/                   # store output images and used for eventual  web documentation
        output/             # store output images from data analises
        pictures/           # store output images from time series analises
        __init__.py   
    logs/       
    src/                    # main source files
        helpers/            # main source files
            __init__.py
            args.py         # auxiliy function, parse_args(), to parse args commands, used on main_signals.py & main_opt.py
            datafeed.py     # auxiliary function, pandasdatafeed(), to read source files, used on main_signals.py & main_opt.py
            main.py         # sample file used to validate functions integration, and initial setup
        __init__.py    
        main_opt.py         # main source files for optimizing strategies/signals params and analyzing it. 
        main_signals.py     # main source files for testing strategies
        settings.py         # setting files with optimaztion params, source file paths, outputs and others
        signals.py          # signals, based on tecnical indicators, used on strategies.py
        strategies.py       # strategies used on main_signals.py & main_opt.py
    testes/                 # tests
        samples/
        __init__.py
        context.py          # context files used on test to import libraries nad insert filepaths from src
        test_data.py        # test file for data/analysis/data.py
        test_data_alysis.py # test file for data/analysis/data_analysis.py
        test_main.py        # test file for src/helpers/main.py
        test_main_opt.py    # test file for src/main_opt.py
    .gitignore
    desktop.ini
    CITATION.cff
    LICENSE.md
    README.md
    requirements.txt
```

___


## How to get data source file

* To generate the timeseries dataset is necessary to compile the script `coletar_mini_xp.mql5` on Metatrader in order to generate the ".ex5" file and then run it.
the files and scripts necessary are under `data\samples\samples.rar`

* To access the MetaQuotes, the script editor in Metatrader, press F4 on the main window

* In order to change the security collected you need to change the variable `nome_ativo`, for example:
``
string nome_ativo= "WIN$N"
``.
You can find some other examples commented on the mentioned file.

___


## How to use `data\analysis`

* you can find in this folder, the source file that can be used to structure data source: `data\analysis\data.py`

* you can find as well, the jupiter notebook file to make the data analysis on the source data: `data\analysis\data_analysis.ipynb`
  * all the functions used to structure and aggregate the data can be found in: `data\analysis\data_analysis.py`

* there is another file, very useful to generate outputs from the optimized params and outputs: `data\analysis\analyzers.py`

## How to use

**obs**: if you get the message ``ImportError: cannot import name 'warnings' from 'matplotlib.dates' `` 
while running the program, remove the `warning` import on `backtrader/plot/locator.py`

**obs**: if you get the message ``ModuleNotFoundError: No module named 'src'`` while running the program, try using:
``python -m src.main`` or any other file you are trying to use.


### How to use for initial uses/samples

Run on the terminal from main repository directory:
``python ./src/helpers/main.py``.

This file is just used to get familiar with the project structure and classes used.


### How to use training/optimization

On the `src` directory, the `main_opt.py` is the module for optimization, using the `settings.json` file as input parameters.


### How to use after getting optimized params

On the `src` directory, the `main_signals.py` is the module for optimization, using the `settings.json` and `data\analyzers_opt\*` files as input parameters.


___


## How to configure

1. Create a **Strategy**. More info can be found here [strategy](https://www.backtrader.com/docu/strategy/)
   * Decide on potential adjustable parameters.
   * Instantiate the Indicators you need in the Strategy
   * Write down the logic for entering/exiting the market
   * Or alternatively:
      * Prepare some indicators to work as long/short signals
   
   A **Cerebro** instance is the pumping heart and controlling brain of backtrader. 
   A **Strategy** is the same for the platform user.
     
   
2. Create a `Cerebro` Engine. More info here [cerebro](https://www.backtrader.com/docu/cerebro/)
   * First: Inject the `Strategy` (or signal-based strategy)   
   And then:
   * Load and Inject a Data Feed (once created use `cerebro.adddata`)
   * And execute `cerebro.run()`
   * For visual feedback use: `cerebro.plot()`
   
   This class is the cornerstone of backtrader because it serves as a central point for
   1. Gathering all inputs (**Data Feeds**), actors (**Stratgegies**), spectators (**Observers**), critics (**Analyzers**) and documenters (**Writers**) ensuring the show still goes on at any moment.
   2. Execute the backtesting/or live data feeding/trading
   3. Returning the results
   4. Giving access to the plotting facilities
   

3. Some other [concepts](https://www.backtrader.com/docu/concepts/) are relevant to understand as well, such as:
   * [datafeed](https://www.backtrader.com/docu/datafeed/), relevant to load data from different sources.
      **Data feeds** are added to **Cerebro** instances and end up being part of the input of strategies
   * [analyzers](https://www.backtrader.com/docu/analyzers/analyzers/), to analyze the performance of the trading system.
   * [observers](https://www.backtrader.com/docu/observers-and-statistics/observers-and-statistics/), Due to observers, all backtrader sample charts have so far had 3 things plotted:
      Cash and Value (what’s happening with the money in the broker);
      Trades (aka Operations);
      Buy/Sell Orders
   * [Indicators](https://www.backtrader.com/docu/induse/), Over 122 indicators with the usual suspects on board, with **ta-lib** integration
   * [order](https://www.backtrader.com/docu/order/),  translate the decisions made by the logic in a Strategy into a message suitable for the Broker to execute an action.
   * [broker](https://www.backtrader.com/docu/broker/), supports different order types, checking a submitted order cash requirements against current cash, keeping track of cash and value for each iteration of cerebro and keeping the current position on different datas.
      Here you can understand some other params such as slippage, cheat-on-open, position and how the trade is made.
   * [Commissions: Stocks vs Futures](https://www.backtrader.com/docu/commission-schemes/commission-schemes/), as different commission schemes can be applied to the same data set.
   

The platform is highly configurable

Let’s hope you, the user, find the platform useful and fun to work with

For some quick start examples please refer to [Backtrader quickstart](https://www.backtrader.com/docu/quickstart/quickstart/)  

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

## How to Install/ Setup enviroment
python
```
where python
which python3
python --version
python -V
```

venv
```
python3 -m pip install --upgrade pip
pip3 install virtualenv
pip3 install --upgrade setuptools

python -m venv ./venv
# or 
"C:\Users\<username>\AppData\Local\Programs\Python\Python39\python.exe" -m venv ./venv
# or 
virtualenv -p ./venv venv

deactivate
conda deactivate

source ./venv/Scripts/activate
# or
./venv/Scripts/activate

pip3 install -r requirements.txt
 
rm -r venv # remove directory
```



#### backtrader
backtrader is self-contained with no external dependencies (except if you want to plot)
```
pip install backtrader
# or
pip install backtrader[plotting]
```

For more infromations please refer to [Backtrader installation](https://www.backtrader.com/docu/installation/)

### Useful Commands

git
```
git status
git rm -rf --cached .    #Clear Entire Git Cache
```
create alias on bash
```
cd
echo alias ll=\'ls -l\' >> .bashrc
echo alias act=\'source ./venv/Scripts/activate\' >> .bashrc
```

#References

[Backtrader](https://www.backtrader.com/)

[Backtrader Github](https://github.com/mementum/backtrader)

[Metatrader Docs.](https://www.mql5.com/pt/docs)

[Backtrader for Backtesting (Python) – A Complete Guide](https://algotrading101.com/learn/backtrader-for-backtesting/)

[What is a Walk-Forward Optimization and How to Run It?](https://algotrading101.com/learn/walk-forward-optimization/)

[What is Overfitting in Trading?](https://algotrading101.com/learn/what-is-overfitting-in-trading/)