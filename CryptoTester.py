import cbpro
import os
import websocket
import pprint
import ta
import numpy as np
import pandas as pd
import cbpro, time
public_client = cbpro.PublicClient()

#coinbase setup
trade_symbol = "ETH-USD"
traded_quantity = .05
cbpro_fee = .005

#rsi setup
rsi_period = 14
rsi_overbought = 70
rsi_oversold = 30

#data storage setup
prices = []
volumes = []
open_position = False
total_buys = 0
total_sells = 0
order_book = {}
order_book['volume'] = []
# order_book['rsiBUY'] = []
# order_book['priceBUY'] = []
# order_book['priceSELL'] = []
# order_book['rsiSELL'] = []
# order_book['quantityPriceBUY'] = []
# order_book['quantityPriceSELL'] = []
# order_book['feeBUY'] = []
# order_book['feeSELL'] = []

#inherit from the cbpro websocket client
class myWebsocketClient(cbpro.WebsocketClient):

    #what to do when we first initially start the client
    def on_open(self):
        self.url = "wss://ws-feed.pro.coinbase.com/"
        self.products = trade_symbol
        self.channels = ["ticker"] #ticker, heartbeat, level2
        print(f"{trade_symbol} RSI Trading Bot has begun!")

    #what to do for each row of data that is reserved to our client from the websocket source (server)
    def on_message(self, msg):

        global prices, open_position, total_buys, total_sells, volume_24h
        try:
        #     #start trying to gather up the price data into an array.
            volumes.append(float(msg['volume_24h']))
        #     #data interval (5min)
        #     #time.sleep(300)
        #
        except:
            pass
        if len(volumes) % 10 == 0 and len(volumes) > 10:
            print(volumes[-10] - volumes[-1])
        #Get enough data in our prices array to then start calculating RSI and trading on that calculation
        # if len(prices) > rsi_period:
        #     np_prices = np.array(prices)
        #     ser = pd.Series(np_prices)
        #     rsi = ta.momentum.rsi(ser, rsi_period, False)
        #     last_rsi = rsi.iloc[-1]
            #print("Current Price: ", float(msg['price'])," | Current RSI: {}".format(last_rsi))

            #overbought trading order (sell high)
            # if last_rsi > rsi_overbought:
            #     if open_position:
            #         print("Overbought! SELL!")
            #         order_book['rsiSELL'].append(last_rsi)
            #         order_book['priceSELL'].append(float(msg['price']))
            #         order_book['quantityPriceSELL'].append(float(msg['price'])*traded_quantity)
            #         order_book['feeSELL'].append(float(msg['price'])*traded_quantity*cbpro_fee)
            #         open_position = False
            #         total_sells+=1
            #         print("Number of Sells: ", total_sells, " at an RSI of ", last_rsi)
            #     else:
            #         pass
            #         #print("You don't own anything.")
            #
            # #oversold trading order (buy low)
            # if last_rsi < rsi_oversold:
            #     if open_position:
            #         pass
            #         #print("You already own it.")
            #     else:
            #         print("Oversold! BUY!")
            #         order_book['rsiBUY'].append(last_rsi)
            #         order_book['priceBUY'].append(float(msg['price']))
            #         order_book['quantityPriceBUY'].append(float(msg['price'])*traded_quantity)
            #         order_book['feeBUY'].append(float(msg['price'])*traded_quantity*cbpro_fee)
            #         open_position = True
            #         total_buys+=1
            #         print("Number of Buys: ", total_buys, " at an RSI of ", last_rsi)

    #lets grab our results when we decide to close our websocket connection
    def on_close(self):
        print("------------ Results ------------\n")
        results = pd.DataFrame(dict([ (k,pd.Series(v)) for k,v in order_book.items() ]))
        results['returnsBeforeFees'] = results.quantityPriceSELL - results.quantityPriceBUY
        results['returnsAfterFees'] = results.quantityPriceSELL - results.quantityPriceBUY - results.feeBUY - results.feeSELL
        print(results)
        print('\n Total returns before Fees: ',results.returnsBeforeFees.sum())
        print('\n Total returns after Fees: ', results.returnsAfterFees.sum())
        #print(prices)

wsClient = myWebsocketClient()
wsClient.start()