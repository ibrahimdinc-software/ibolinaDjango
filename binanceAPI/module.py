import pandas as pd
import numpy as np

from datetime import datetime, timedelta

from binance.exceptions import BinanceAPIException
from binance import Client
from binance import ThreadedWebsocketManager
from ray import client

from binanceAPI.models import BinanceApiModel


class BinanceAPIModule():

    def __init__(self, bam=None):
        self.bam = BinanceApiModel.objects.filter(user=1)[0] if not bam else bam
        self.client = Client(self.bam.apiKey, self.bam.apiSecretKey)
        print("module initialized")

    def openPosOrder(self, pair, price, size, side, positionSide):
        quantity = self.calcQuantityPrecision(pair, size/price)

        if quantity != "0":
            order = None
            try:
                order = self.client.futures_create_order(
                    symbol=pair,
                    side=side,
                    positionSide=positionSide if self.bam.hedgeMode else None,
                    type='MARKET',
                    quantity=quantity,
                    recvWindow=50000
                )
            except BinanceAPIException as e:
                print(e.message)
            
            print("order created")
            return quantity, order
        return None

    def closePosOrder(self, pair, quantity, side, positionSide):
        order = None
        try:
            order = self.client.futures_create_order(
                symbol=pair,
                side=side,
                positionSide=positionSide if self.bam.hedgeMode else None,
                type='MARKET',
                quantity=quantity,
                recvWindow=50000
            )
        except BinanceAPIException as e:
            print(e.message)
        
        print("order created")
        return order
    
    def getPoisitionMode(self):
        return self.client.futures_get_position_mode()['dualSidePosition']

    def getSymbolInfo(self):
        symbolInfo = pd.DataFrame(self.client.futures_exchange_info()["symbols"])
        return symbolInfo

    def calPricePrecision(self, pair, price, symbolInfo):
        symbolInfo = pd.DataFrame(self.client.futures_exchange_info()["symbols"])
        symbolInfo = pd.DataFrame(symbolInfo.loc[symbolInfo["symbol"]==pair]["filters"].values[0])
        stepSize = float(symbolInfo.loc[symbolInfo["filterType"]=="PRICE_FILTER"].tickSize.values[0])
        stepSize = int(np.floor(np.abs(np.log10(stepSize))))
        price = round(price, stepSize)
        print("calc price", price)
        return price

    def calcQuantityPrecision(self, pair, quantity):
        symbolInfo = self.getSymbolInfo()
        symbolInfo = pd.DataFrame(symbolInfo.loc[symbolInfo["symbol"]==pair]["filters"].values[0])
        stepSize = float(symbolInfo.loc[symbolInfo["filterType"]=="LOT_SIZE"].stepSize)
        diff = float(quantity) % stepSize
        q = quantity - diff
        print("calc quantity", q)
        return q

    def getBalance(self):
        balances = self.client.futures_account_balance(recvWindow = 50000)
        balances = pd.DataFrame(balances)
        balances = balances.loc[balances["asset"]=="USDT"]
        balance = float(balances.balance.values[0])
        print("get balance: "+str(balance))
        return balance

    def getOpenOrders(self, symbol, type):
        orders = pd.DataFrame(self.client.futures_get_open_orders(recvWindow = 50000, symbol=symbol))
        orders = orders.loc[orders["origType"]==type]
        return orders

    def setLeverage(self, pair):
        try:
            self.client.futures_change_leverage(recvWindow = 50000, symbol=pair, leverage=25)
        except BinanceAPIException as e:
            pass

        try :
            self.client.futures_change_margin_type(recvWindow = 50000, symbol=pair, marginType="CROSS")
        except BinanceAPIException as e:
            pass
    
    def getKline(self, symbol, size, interval):
        date = datetime.now()

        startStr = (date - timedelta(hours=size+6)).strftime('%Y-%m-%d %H:%M')
        endStr = (date + timedelta(hours=3)).strftime('%Y-%m-%d %H:%M')

        data = self.client.futures_historical_klines(
            symbol=symbol,
            interval=interval,
            start_str=startStr,
            end_str=endStr
        )

        df = pd.DataFrame(data, columns=['Open Time', 'Open', 'High', 'Low', 'Close', 'Real Leverage', 'Close Time', 'Ignore', 'Number of NAV Update', 'Ignore', 'Ignore', 'Ignore'], dtype=float)
        df.drop(['Real Leverage', 'Ignore', 'Number of NAV Update'], axis=1, inplace=True)
        df['Open Time'] = df['Open Time'] / 1000
        df['Close Time'] = df['Close Time'] / 1000

        df['Open Time'] = pd.to_datetime(df['Open Time'], unit='s') + timedelta(hours=3)
        df['Close Time'] = pd.to_datetime(df['Close Time'], unit='s') + timedelta(hours=3)
        

        
        return df

    def getPositionInfo(self, pair):
        info = self.client.futures_position_information(recvWindow=50000, symbol=pair)[0]
        
        if float(info["entryPrice"]) > float(info["liquidationPrice"]):
            return {
                "side": "long",
                "amount": float(info["positionAmt"])
            }
        elif float(info["entryPrice"]) < float(info["liquidationPrice"]):
            return {
                "side": "short",
                "amount": float(info["positionAmt"])
            }

        return None

    def klineListener(self):
        twm = ThreadedWebsocketManager(self.bam.apiKey, self.bam.apiSecretKey)
        return twm



class BotActionModule():

    def __init__(self, bams: BinanceAPIModule, pairModel):
        self.bams = bams
        self.pairModel = pairModel

    def getPairPosModel(self, baModule):

        ppm = self.pairModel.pairposmodel_set.filter(
            bam=baModule.bam,
            pair=self.pairModel
        )[0]

        return ppm

    def openPosition(self, openPosPrice, positionSide):
        for bam in self.bams:
            bam.setLeverage(self.pairModel.pair)
            posSize = bam.getBalance() * 0.02 * 25
            q, o = bam.openPosOrder(
                pair=self.pairModel.pair,
                price=openPosPrice,
                size=posSize,
                side='BUY' if positionSide == 'LONG' else 'SELL',
                positionSide=positionSide
            )
            ppm = self.getPairPosModel(bam)
            ppm.quantity = q
            ppm.save()

            print(f'{self.pairModel.pair} | Open {positionSide.lower()} pos order created for {bam.bam.name}')

    def closePosition(self, positionSide, quantityPercentage):
        for bam in self.bams:
            ppm = self.getPairPosModel(bam)

            quantity = ppm.quantity * quantityPercentage
            quantity = bam.calcQuantityPrecision(self.pairModel.pair, quantity) if quantityPercentage != 1 else quantity

            bam.closePosOrder(
                pair=self.pairModel.pair,
                quantity=quantity,
                side='SELL' if positionSide == 'LONG' else 'BUY',
                positionSide=positionSide
            )

            ppm.quantity = ppm.quantity - quantity
            ppm.save()

            print(f'{self.pairModel.pair} | Close {"all" if quantityPercentage==1 else "half"} of {positionSide.lower()} pos order created for {bam.bam.name}')

