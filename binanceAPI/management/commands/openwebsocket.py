from datetime import timedelta
from django.core.management.base import BaseCommand
from binance import ThreadedWebsocketManager
import pandas as pd
from binanceAPI.botModule import BotModule
from binanceAPI.models import KlineIndicatorModel, PairModel
from binanceAPI.module import BinanceAPIModule
from techAnalys.module import IndicatorCalculatorModule

class Command(BaseCommand):
    def handle(self, *args, **options):
        pm = PairModel.objects.get(pair="FTMUSDT")
        kims = pm.klineindicatormodel_set.all().reverse()[:max([pm.bigDonLen, pm.smallDonLen, pm.emaLen])]

        kims = pd.DataFrame.from_records(kims.values())
        

        api_key = "wSoKWo39yJEs6FB5WFFg0DppHJBF24Mnf6GLsLchUouqfNTlLppRdwgBEp7croYz"
        sec_key = "FPaw5AXXAi07SYyzSRv4N9FPHiytcy2tXJePiLEunAwdj8fgaiRJjNkD4KbHPyAZ"

        self.twm = ThreadedWebsocketManager(api_key, sec_key)
        self.twm.start()
        print('twm started')

        symbol = 'FTMUSDT'

        def handleSocketMessage(msg):
            candle = msg['k']
            isCandleClosed = True #candle['x']
            candleDatas = None
            if isCandleClosed:
                candleDatas = {
                    'Open Time': candle['t'],
                    'Close Time': candle['T'],
                    'Open': float(candle['o']),
                    'High': float(candle['h']),
                    'Low': float(candle['l']),
                    'Close': float(candle['c']),
                }
                print(candleDatas.values(), candleDatas.keys())
                newCandle = pd.DataFrame(candleDatas, index=[0])
                newCandle = IndicatorCalculatorModule(bigDonLen=pm.bigDonLen, smallDonLen=pm.smallDonLen, 
                                                emaLen=pm.emaLen).newCandleIndicatorCalc(kims, newCandle)
                print(newCandle.head())
                newCandle['Open Time'] = newCandle['Open Time'] / 1000
                newCandle['Close Time'] = newCandle['Close Time'] / 1000

                newCandle['Open Time'] = pd.to_datetime(newCandle['Open Time'], unit='s') + timedelta(hours=3)
                newCandle['Close Time'] = pd.to_datetime(newCandle['Close Time'], unit='s') + timedelta(hours=3)
                
                KlineIndicatorModel.objects.get_or_create(
                    pair = self,
                    openTime=newCandle['Open Time'], 
                    closeTime=newCandle['Close Time'],
                    open = newCandle['Open'],
                    high = newCandle['High'],
                    low = newCandle['Low'],
                    close = newCandle['Close'],
                    bigDonUB = newCandle['BigUB'],
                    bigDonLB = newCandle['BigLB'],
                    smallDonUB = newCandle['SmallUB'],
                    smallDonLB = newCandle['SmallLB'],
                    ema = newCandle['ema']
                )
                
        print('starting socket')
        self.twm.start_kline_futures_socket(handleSocketMessage, symbol, '1m')

        self.twm.join()
        



