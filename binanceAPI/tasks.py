import asyncio
import json
from ibolinaDjango.celery import app
from .models import BinanceApiModel, PairModel
from binanceAPI.module import BinanceAPIModule
from binanceAPI.botModule import BotModule

import websocket

@app.task(bind=True, name='new-candle-provider')
def newCandleProvider(self):
    pms = PairModel.objects.all()
    for pm in pms:
        pm.getDatas()
        print(f'Datas get for {pm.pair}')

@app.task(bind=True, name="binanceListener")
def binanceListener(self):
    pms = PairModel.objects.all()
    bams = [BinanceAPIModule(bam) for bam in BinanceApiModel.objects.all() if bam.isActive]
    botModule = {pm.pair: BotModule(pm.pair, bams) for pm in pms}

    streams = [f'{pm.pair.lower()}@kline_{pm.interval}' for pm in pms]
    SOCKET = f'wss://fstream.binance.com/stream?streams={"/".join(streams)}'

    def on_open(ws):
        print('opened connection')


    def on_close(ws):
        print('closed connection')

    def on_message(ws, msg):
        print(json.loads(msg))

    def callback(ws, msg):
        candle = msg['data']['k']
        isCandleClosed = candle['x']

        botModule[candle['s']].control(candle['c'])        

        if isCandleClosed:
            botModule[candle['s']].createNewCandle(
                {
                    'openTime': candle['t'],
                    'closeTime': candle['T'],
                    'open': float(candle['o']),
                    'high': float(candle['h']),
                    'low': float(candle['l']),
                    'close': float(candle['c']),
                }
            )
    
    ws = websocket.WebSocketApp(SOCKET, on_open=on_open, on_close=on_close, on_message=on_message)
    ws.run_forever()


@app.task(bind=True, name="closePosition")
def closePositionTask(self, binanceApiModule, botActionModule, positionSide, quantityPercentage):
    print('Close position task running.')

    ppm = botActionModule.getPairPosModel(binanceApiModule)

    quantity = ppm.quantity * quantityPercentage
    quantity = binanceApiModule.calcQuantityPrecision(botActionModule.pairModel.pair, quantity) if quantityPercentage != 1 else quantity

    binanceApiModule.closePosOrder(
        pair=botActionModule.pairModel.pair,
        quantity=quantity,
        side='SELL' if positionSide == 'LONG' else 'BUY',
        positionSide=positionSide
    )

    ppm.quantity = ppm.quantity - quantity
    ppm.save()

    print(f'{botActionModule.pairModel.pair} | Close {"all" if quantityPercentage==1 else "half"} of {positionSide.lower()} pos order created for {binanceApiModule.bam.name}')


    print('Close position task finished.')


    



