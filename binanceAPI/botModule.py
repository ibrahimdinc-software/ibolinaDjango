import pandas as pd

from datetime import datetime, timedelta

from binanceAPI.models import BinanceApiModel, KlineIndicatorModel, PairModel
from binanceAPI.module import BinanceAPIModule, BotActionModule
from paperTrade.module import PaperTradeModule
from techAnalys.module import IndicatorCalculatorModule

class BotModule():    
    
    def __init__(self, pair, bams):
        self.pair = pair
        self.pairModel = PairModel.objects.get(pair=pair)
        self.rrRatio = self.pairModel.rrRatio
        self.lastCandle = self.getLastCandle()
        self.previousCandle = self.getPreviousCandle()
        self.firstTpModel, self.secondTpModel  = self.getTpModels()
        self.bams = bams

        print(self.firstTpModel, self.secondTpModel)

    def getLastCandle(self):
        lastCandle = self.pairModel.klineindicatormodel_set.filter(pair=self.pairModel)
        lastCandle = lastCandle.order_by('-openTime')[0]
        return lastCandle

    def getPreviousCandle(self):
        previousCandle = self.pairModel.klineindicatormodel_set.filter(pair=self.pairModel)
        previousCandle = previousCandle.order_by('-openTime')[1]
        return previousCandle

    def getTpModels(self):
        tpModels = self.pairModel.pairtpmodel_set.all()
        return [tpm for tpm in tpModels]

    def createNewCandle(self, candleDatas:dict):
        selTo = max(
            [self.pairModel.pMaxLen, 
            self.pairModel.pMaxMultiplier, 
            self.pairModel.emaLen+30,
            self.pairModel.hmaLen+30]
        ) + 5
        kims = self.pairModel.klineindicatormodel_set.filter(pair=self.pairModel).order_by('-openTime')[:selTo]
        print(f'{self.pairModel.pair} | New Candle')
        kims = pd.DataFrame.from_records(kims.values())
        kims = kims.sort_values(['openTime'])
        newCandle = pd.DataFrame(candleDatas, index=[0])
        newCandle = IndicatorCalculatorModule(
            pMaxLen=self.pairModel.pMaxLen, 
            pMaxMultiplier=self.pairModel.pMaxMultiplier, 
            emaLen=self.pairModel.emaLen, 
            hmaLen=self.pairModel.hmaLen
        ).newCandleIndicatorCalc(kims, newCandle)
        
        newCandle['openTime'] = newCandle['openTime'] / 1000
        newCandle['closeTime'] = newCandle['closeTime'] / 1000

        newCandle['openTime'] = pd.to_datetime(newCandle['openTime'], unit='s') + timedelta(hours=3)
        newCandle['closeTime'] = pd.to_datetime(newCandle['closeTime'], unit='s') + timedelta(hours=3)
        

        kim, created = KlineIndicatorModel.objects.get_or_create(
                pair = self,
                openTime=  newCandle['openTime'], 
                closeTime= newCandle['closeTime'],
                open =     newCandle['open'],
                high =     newCandle['high'],
                low =      newCandle['low'],
                close =    newCandle['close'],
                var =      newCandle['var'],
                pmax =     newCandle['pmax'],
                hma =      newCandle['hma'],
            )


        self.pairModel.cooldownDate = None
        self.pairModel.save()

        self.previousCandle = self.lastCandle
        self.lastCandle = kim
     
    def calcPercentage(self, firstPrice, lastPrice):
        return 100*(lastPrice-firstPrice)/firstPrice

    def calcTpPrice(self, openPrice, stopPrice, rrRatio):
        return openPrice + ((-self.calcPercentage(openPrice, stopPrice)*rrRatio)*openPrice /100)

    def enterLongPosCond(self, candleClose):
        conditions = [
            candleClose > self.lastCandle.pmax,
            self.lastCandle.high < self.lastCandle.pmax,
            self.lastCandle.var < self.lastCandle.pmax,
            self.pairModel.cooldownDate == None,
            self.pairModel.inPos == 'NONE'
        ]
        return all(conditions)

    def closeLongPosCond(self, candleClose):
        conditions = [
            candleClose < self.lastCandle.pmax,
            self.lastCandle.low > self.lastCandle.pmax,
            self.lastCandle.var > self.lastCandle.pmax,
            self.pairModel.inPos == 'LONG',
            self.pairModel.trailingClose
        ]
        return all(conditions)

    def enterShortPosCond(self, candleClose):
        conditions = [
            candleClose < self.lastCandle.pmax,
            self.lastCandle.low > self.lastCandle.pmax,
            self.lastCandle.var > self.lastCandle.pmax,
            self.pairModel.cooldownDate == None,
            self.pairModel.inPos == 'NONE'
        ]
        return all(conditions)

    def closeShortPosCond(self, candleClose):
        conditions = [
            candleClose > self.lastCandle.pmax,
            self.lastCandle.high < self.lastCandle.pmax,
            self.lastCandle.var < self.lastCandle.pmax,
            self.pairModel.inPos == 'SHORT',
            self.pairModel.trailingClose
        ]
        return all(conditions)

    def stopLongPosCond(self, candleClose):
        conditions = [
            candleClose <= self.pairModel.stopPrice if self.pairModel.stopPrice else False,
            self.pairModel.inPos == 'LONG'
        ]
        return all(conditions)

    def stopShortPosCond(self, candleClose):
        conditions = [
            candleClose >= self.pairModel.stopPrice if self.pairModel.stopPrice else False,
            self.pairModel.inPos == 'SHORT'
        ]
        return all(conditions)

    def medTpCond(self, candleClose, tpModel):
        cond1 = [
            candleClose >= tpModel.tpPrice if tpModel.tpPrice else False,
            self.pairModel.inPos == 'LONG',
            not tpModel.isTaken
        ]
        cond2 = [
            candleClose <= tpModel.tpPrice if tpModel.tpPrice else False,
            self.pairModel.inPos == 'SHORT',
            not tpModel.isTaken
        ]
        conditions = [
            all(cond1),
            all(cond2)
        ]
        return any(conditions)

    def lastTpCond(self, candleClose):
        conditions = [
            (candleClose >= self.pairModel.tpPrice if self.pairModel.tpPrice else False) and self.pairModel.inPos == 'LONG',
            (candleClose <= self.pairModel.tpPrice if self.pairModel.tpPrice else False) and self.pairModel.inPos == 'SHORT'
        ]
        return any(conditions)

    def setPosStatus(self, side):
        openPosPrice = self.lastCandle.pmax
        stopPrice = self.lastCandle.var

        self.pairModel.entryPrice = openPosPrice
        self.pairModel.stopPrice = stopPrice
        self.pairModel.tpPrice = self.calcTpPrice(openPosPrice, stopPrice, self.rrRatio)
        self.pairModel.inPos = side
        self.pairModel.save()

        print(f'Setting TP Model {self.firstTpModel}')
        self.firstTpModel.tpPrice = self.calcTpPrice(openPosPrice, stopPrice, self.rrRatio*self.firstTpModel.tpRate)
        self.firstTpModel.save()

        print(f'Setting TP Model {self.secondTpModel}')
        self.secondTpModel.tpPrice = self.calcTpPrice(openPosPrice, stopPrice, self.rrRatio*self.secondTpModel.tpRate)
        self.secondTpModel.save()

        return openPosPrice

    def resetPairModel(self):
        self.pairModel.inPos = 'NONE'
        self.pairModel.stopPrice = None
        self.pairModel.tpPrice = None
        self.pairModel.save()

        self.firstTpModel.tpPrice = None
        self.firstTpModel.isTaken = False
        self.firstTpModel.save()

        self.secondTpModel.tpPrice = None
        self.secondTpModel.isTaken = False
        self.secondTpModel.save()


    def control(self, candleClose):
        candleClose = float(candleClose)
        if self.enterLongPosCond(candleClose):
            # OPEN POS

            openPosPrice = self.setPosStatus('LONG')

            BotActionModule(self.bams, self.pairModel).openPosition(openPosPrice, 'LONG')
            PaperTradeModule(self.pairModel, 'LONG').createPos()

            print(f'{self.pairModel.pair} | Enter {self.pairModel.inPos} position from {openPosPrice}')
        elif self.stopLongPosCond(candleClose):
            # STOP POS
            
            print(f'{self.pairModel.pair} | Stop {self.pairModel.inPos} position from {self.pairModel.stopPrice}')
            
            BotActionModule(self.bams, self.pairModel).closePosition('LONG', 1)

            self.resetPairModel()
        elif self.closeLongPosCond(candleClose):
            # CLOSE POS
            
            print(f'{self.pairModel.pair} | Close {self.pairModel.inPos} position from {candleClose}')

            BotActionModule(self.bams, self.pairModel).closePosition('LONG', 1)

            self.resetPairModel()
            
        elif self.enterShortPosCond(candleClose):
            # OPEN POS

            openPosPrice = self.setPosStatus('SHORT')

            BotActionModule(self.bams, self.pairModel).openPosition(openPosPrice, 'SHORT')

            print(f'{self.pairModel.pair} | Enter {self.pairModel.inPos} position from {openPosPrice}')
        elif self.stopShortPosCond(candleClose):
            # STOP POS

            print(f'{self.pairModel.pair} | Stop {self.pairModel.inPos} position from {self.pairModel.stopPrice}')
            
            BotActionModule(self.bams, self.pairModel).closePosition('SHORT', 1)
            
            self.resetPairModel()
        elif self.closeShortPosCond(candleClose):
            # CLOSE POS

            print(f'{self.pairModel.pair} | Close {self.pairModel.inPos} position from {candleClose}')
            
            BotActionModule(self.bams, self.pairModel).closePosition('SHORT', 1)

            self.resetPairModel()

        elif self.medTpCond(candleClose, self.firstTpModel):
            # TAKE PROFIT

            print(f'{self.pairModel.pair} | First Take profit {self.pairModel.inPos} position from {self.firstTpModel.tpPrice}')

            BotActionModule(self.bams, self.pairModel).closePosition(self.pairModel.inPos, 0.25)
        
            self.pairModel.stopPrice = self.pairModel.entryPrice
            self.pairModel.save()
            self.firstTpModel.isTaken = True
            self.firstTpModel.save()

        elif self.medTpCond(candleClose, self.secondTpModel):
            # TAKE PROFIT

            print(f'{self.pairModel.pair} | Second Take profit {self.pairModel.inPos} position from {self.secondTpModel.tpPrice}')

            BotActionModule(self.bams, self.pairModel).closePosition(self.pairModel.inPos, 0.5)
        
            self.pairModel.stopPrice = self.firstTpModel.tpPrice
            self.pairModel.save()
            self.secondTpModel.isTaken = True
            self.secondTpModel.save()


        elif self.lastTpCond(candleClose):
            # TAKE PROFIT

            print(f'{self.pairModel.pair} | Take profit {self.pairModel.inPos} position from {self.pairModel.tpPrice}')

            BotActionModule(self.bams, self.pairModel).closePosition(self.pairModel.inPos, 1)
            
            self.pairModel.cooldownDate = datetime.now()
            self.resetPairModel()




