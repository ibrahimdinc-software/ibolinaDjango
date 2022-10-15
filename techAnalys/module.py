import pandas as pd
import pandas_ta as ta
import numpy as np
import math

from ta.volatility import AverageTrueRange
from ta.trend import EMAIndicator, WMAIndicator
from binanceAPI.module import BinanceAPIModule


class IndicatorCalculatorModule():

    def __init__(self, symbol=None, pMaxLen=None, pMaxMultiplier=None, emaLen=None, hmaLen=None, interval=None) -> None:
        self.symbol = symbol
        self.pMaxLen = pMaxLen
        self.pMaxMultiplier = pMaxMultiplier
        self.emaLen = emaLen
        self.hmaLen = hmaLen
        self.interval = interval
    
    def tema(self, dfClose, window):
        ema1 = EMAIndicator(dfClose, window).ema_indicator()
        ema2 = EMAIndicator(ema1, window).ema_indicator()
        ema3 = EMAIndicator(ema2, window).ema_indicator()

        return 3*(ema1-ema2)+ema3

    def hullma(self, dfClose, window):
        hullma = WMAIndicator(2*WMAIndicator(dfClose, math.floor(window/2)).wma()-WMAIndicator(dfClose, window).wma(), math.floor(math.sqrt(window))).wma()
        return hullma 

    def pMax(df, atrPeriod, atrMultiplier):
        atr = AverageTrueRange(df['High'], df['Low'], df['Close'], atrPeriod).average_true_range()
        df['atr'] = atr
        
        prevFinalUB = 0
        prevFinalLB = 0
        finalUB = 0
        finalLB = 0
        prevVar = 0
        prevPMax = 0
        pmax= []
        pmaxC = 0

        for index, row in df.iterrows():
            if not np.isnan(row['Close']):
                atrC = row['atr'] if not math.isnan(row['atr']) else 0
                varC = row['var']

                basicUB = varC + atrMultiplier * atrC
                basicLB = varC - atrMultiplier * atrC

                if basicUB < prevFinalUB or prevVar > prevFinalUB:
                    finalUB = basicUB
                else:
                    finalUB = prevFinalUB
                
                if basicLB > prevFinalLB or prevVar < prevFinalLB:
                    finalLB = basicLB
                else:
                    finalLB = prevFinalLB

                if prevPMax == prevFinalUB and varC <= finalUB:
                    pmaxC = finalUB
                else:
                    if prevPMax == prevFinalUB and varC >= finalUB:
                        pmaxC = finalLB
                    else:
                        if prevPMax == prevFinalLB and varC >= finalLB:
                            pmaxC = finalLB
                        elif prevPMax == prevFinalLB and varC <= finalLB:
                            pmaxC = finalUB

                pmax.append(pmaxC)
                prevVar = varC
                prevFinalUB = finalUB
                prevFinalLB = finalLB
                prevPMax = pmaxC

        return pmax

    def calcIndicators(self) -> pd.DataFrame:
        size = max([self.pMaxLen, self.pMaxMultiplier, self.emaLen+30, self.hmaLen+30])
        df = BinanceAPIModule().getKline(self.symbol, size, self.interval)

        df['var'] = df.ta.vidya(close=(df['High']+df['Low'])/2, length=self.emaLen)
        df['pmax'] = self.pMax(df, self.pMaxLen, self.pMaxMultiplier)
        df['hma'] = self.hullma(df['Close'], self.hmaLen)

        df.drop(range(0,size), axis=0, inplace=True)
        df.drop(df.tail(1).index, inplace=True)

        return df


    def newCandleIndicatorCalc(self, oldCandles, newCandle):
        oldCandles = pd.concat([oldCandles, newCandle])

        oldCandles['var'] = oldCandles.ta.vidya(close=(oldCandles['High']+oldCandles['Low'])/2, length=self.emaLen)
        oldCandles['pmax'] = self.pMax(oldCandles, self.pMaxLen, self.pMaxMultiplier)
        oldCandles['hma'] = self.hullma(oldCandles['Close'], self.hmaLen)
        
        return oldCandles.iloc[-1]