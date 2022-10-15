from binanceAPI.models import PairModel
from paperTrade.models import PaperAccountModel, PaperPositionLogModel, PaperPositionModel, PaperPositionQuantityModel



class PaperTradeModule():
    def __init__(self, pairModel, side):
        self.pairModel = pairModel
        self.side = side
        self.paperAccount = PaperAccountModel.objects.first()

    def calcProfit(self):
        pass

    def createPos(self, price):
        paperPosModel = PaperPositionModel.objects.get(
            pair=self.pairModel
        )

        quantity = self.paperAccount.getSize()/price
        paperPosModel.quantity = quantity
        paperPosModel.size = self.paperAccount.getSize()
        paperPosModel.save()

        paperPosLogModel = PaperPositionLogModel.objects.create(
            paperPosition=paperPosModel,
            logType='enter',
            side=self.side,
            price=price,
            quantity=quantity,
            profit=0,
            commision=self.paperAccount.getSize()*0.04
        )

    def stopPosition(self, price):
        paperPosModel = PaperPositionModel.objects.get(
            pair=self.pairModel
        )
        quantity = paperPosModel.quantity

        paperPosLogModel = PaperPositionLogModel.objects.create(
            paperPosition=paperPosModel,
            logType='enter',
            side=self.side,
            price=price,
            quantity=quantity,
            profit=,
            commision=self.paperAccount.getSize()*0.04
        )











