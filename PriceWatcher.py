import cbpro
import os
import websocket
import pprint
import ta
import numpy as np
import pandas as pd
import cbpro, time

import ModuleAgnostic as ma
public_client = cbpro.PublicClient()

# coinbase setup
# trade_symbol = "ETH-USD"
# traded_quantity = .05
# cbpro_fee = .005
#
# # rsi setup
# rsi_period = 14
# rsi_overbought = 70
# rsi_oversold = 30
#
# # data storage setup
# prices = []
# open_position = False
# total_buys = 0
# total_sells = 0
# order_book = {}
# order_book['rsiBUY'] = []
# order_book['priceBUY'] = []
# order_book['priceSELL'] = []
# order_book['rsiSELL'] = []
# order_book['quantityPriceBUY'] = []
# order_book['quantityPriceSELL'] = []
# order_book['feeBUY'] = []
# order_book['feeSELL'] = []


# inherit from the cbpro websocket client
class myWebsocketClient(cbpro.WebsocketClient):
    def __init__(self, url="wss://ws-feed.pro.coinbase.com", products=None, message_type="subscribe", mongo_collection=None,
                 should_print=True, auth=False, api_key="", api_secret="", api_passphrase="", channels=None):
        super().__init__(url, products, message_type, mongo_collection, should_print, auth, api_key, api_secret, api_passphrase, channels)
        self.message_count = 0
        self.df, self.data = self.loadCsvData()
        self.data = [i for i in self.data if i[0] != 'RACA']
        self.coin_tickers = [i[0] + "-USD" for i in self.data] + ['BTC-USD']
        self.data_book = []
        self.current_btc = 0
        pd.set_option('display.max_columns', None)
        # print(self.df)

    def loadCsvData(self):
        df = pd.read_csv("C:\\Users\\colto\\Google Drive\\crypto\\Price_Points.csv", encoding="ISO-8859-1")
        lst = df.to_numpy().tolist()
        return df, lst
    # what to do when we first initially start the client
    def on_open(self):
        self.url = "wss://ws-feed.pro.coinbase.com/"
        self.channels = ["ticker"]
        self.products = self.coin_tickers
    def on_message(self, msg):
        time.sleep(1)
        try:
            if msg['product_id'] == 'BTC-USD':
                self.current_btc = float(msg['price'])
            else:
                self.dataProcessor(msg)
        except:
            pass


    def dataProcessor(self, msg):
        current_id = msg['product_id'][:-4]
        cr_df = self.df[(self.df['CRYPTO'] == current_id)]
        cr_lst = cr_df.to_numpy().tolist()[0]
        current_price = float(msg['price'])
        o_price = cr_lst[5]
        x5Price = o_price * 5
        x10Price = o_price * 10
        x20Price = o_price * 20
        x50Price = o_price * 50
        x5_match = current_price/x5Price
        x10_match = current_price / x10Price
        x20_match = current_price / x20Price
        x50_match = current_price / x50Price

        if x5_match >= 1:
            print("\n_____________________________________", current_id, " at x5")
        if x10_match >= 1:
            print("\n_____________________________________", current_id, " at x10")
        if x20_match >= 1:
            print("\n_____________________________________", current_id, " at x20")
        if x50_match >= 1:
            print("\n_____________________________________", current_id, " at x50")

    # lets grab our results when we decide to close our websocket connection
    # def on_close(self):
    #     print("------------ Results ------------\n")
    #     results = pd.DataFrame(dict([(k, pd.Series(v)) for k, v in order_book.items()]))
    #     results['returnsBeforeFees'] = results.quantityPriceSELL - results.quantityPriceBUY
    #     results['returnsAfterFees'] = results.quantityPriceSELL - results.quantityPriceBUY - results.feeBUY - results.feeSELL
    #
    #     print('\n Total returns before Fees: ', results.returnsBeforeFees.sum())
    #     print('\n Total returns after Fees: ', results.returnsAfterFees.sum())
        # print(prices)

wsClient = myWebsocketClient()
wsClient.start()