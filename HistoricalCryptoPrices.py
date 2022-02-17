import pandas_datareader as web
import datetime as dt
import pandas as pd
import cbpro, time
import openpyxl
import ModuleAgnostic as ma
import requests
import fastquant as fq


def loadCsvData():
    df = pd.read_excel("C:\\Users\\colto\\Google Drive\\crypto\\SatoshiValues.xlsx", dtype='object')
    data = df.to_numpy().tolist()
    # print(data)
    return df, data


def main():
    pd.set_option('display.max_rows', None)
    df_satoshi, data = loadCsvData()
    ma.printLine(data)
    coin_tickers_bin = ['BTC/USDT'] + ['ETH/USDT'] + [i[0] + "/USDT" for i in data]
    coin_tickers_foo = ['BTC-USD'] + ['ETH-USD'] + [i[0] + "-USD" for i in data]
    pd.set_option('display.max_columns', None)
    # historical_btc, historical_eth = parserCoin('BTC-USD'), parserCoin('ETH-USD')
    # print(parserCoin('ALGO-USD'))
    # print(historical_eth)
    # df_coins = pd.merge(historical_btc, historical_eth, on='Date')

    # lst1, lst2 = parserTester(coin_tickers_bin[1]), parserCoin(coin_tickers_foo[1])
    # lst1, lst2 = lst1.to_numpy().tolist(), lst2.to_numpy().tolist()
    # df_starter1 = checkForDuplicateData(lst1, lst2, coin_tickers_bin[1])
    # df_starter.col1 = df_starter.col1.astype(str)
    # df_starter1.col2 = df_starter1.col2.astype(str)
    # out = pd.concat([df_starter, df_starter1], axis=0, ignore_index=True)
    # print(df_starter1.join(df_starter))

    # data = out.to_numpy().tolist()
    # data = [i[0] for i in data]
    # print(len(set(data)))
    lst1, lst2 = parserTester(coin_tickers_bin[0]), parserCoin(coin_tickers_foo[0])
    lst1, lst2 = lst1.to_numpy().tolist(), lst2.to_numpy().tolist()
    df_prices = checkForDuplicateData(lst1, lst2, coin_tickers_bin[0])

    for i in range(1, len(coin_tickers_bin)):
        try:
            lst1, lst2 = parserTester(coin_tickers_bin[i]), parserCoin(coin_tickers_foo[i])
            lst1, lst2 = lst1.to_numpy().tolist(), lst2.to_numpy().tolist()
            #
            df_out = checkForDuplicateData(lst1, lst2, coin_tickers_bin[i])
            df_prices = pd.merge(df_prices, df_out, on='Date')
        except:
            pass


    headers_prices = list(df_prices.columns.values)[1:]
    for i in range(len(headers_prices)):
        name_eth = headers_prices[i] + "/GWEI"
        name_btc = headers_prices[i] + "/SAT"
        df_prices[name_eth] = (df_prices[headers_prices[i]] / df_prices['ETH']) * 1000000000
        df_prices[name_btc] = (df_prices[headers_prices[i]] / df_prices['BTC']) * 100000000
    makeComparisons(df_prices, data)

def makeComparisons(df, data_lst):
    try:
        for i in data_lst:
            data_st = i[1]
            name = i[0] + "/SAT"
            ratio_name = name + "-ratio"

            df[ratio_name] = df[name]/i[1]
        print(df)
    except:
        pass
def checkForDuplicateData(lst1, lst2, coin):
    dates, data_line = [], []
    for i in lst1:
        if i[0] not in dates:
            dates.append(i[0])
            data_line.append(i)
    for i in lst2:
        if i[0] not in dates:
            dates.append(i[0])
            data_line.append(i)

    for i in range(len(data_line)):
        data_line[i][0] = str(data_line[i][0])[:10]
    data_line = sorted(data_line, key=lambda x: x[0])
    df_test = [{'Date': i[0], coin.replace("/USDT", "").replace("-USD", ""): i[1]} for i in data_line]
    df = pd.DataFrame(df_test, columns=['Date', coin.replace("/USDT", "").replace("-USD", "")])
    # print(df)
    return df


def parserTester(coin):
    start = '2021-11-01'
    # end = '2022-02-16'
    end = dt.datetime.now().strftime("%Y-%m-%d")

    dot = fq.get_crypto_data(coin, start, end)
    dot = dot[['close']]
    dot = dot.reset_index()
    coin_name = coin.replace("/USDT", "").replace("-USD", "")
    dot.rename(columns={'close': coin_name, 'dt': 'Date'}, inplace=True)
    return dot


def parserCoin(coin):
    start = dt.datetime(2021, 11, 1)
    end = dt.datetime.now()
    ltc = web.DataReader(coin, 'yahoo', start, end)
    ltc = ltc[['Close']]
    ltc = ltc.reset_index()
    coin_name = coin.replace("/USDT", "").replace("-USD", "")
    ltc.rename(columns={'Close': coin_name}, inplace=True)
    return ltc


main()
