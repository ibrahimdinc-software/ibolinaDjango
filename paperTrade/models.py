from django.db import models

# Create your models here.

LOG_CHOICES = (
    ('enter', 'Enter Pos'),
    ('first', 'First TP'),
    ('second', 'Second TP'),
    ('last', 'Last TP'),
    ('close', 'Close Pos'),
    ('stop', 'Stop Pos'),
)

class PaperAccountModel(models.Model):
    name = models.CharField(verbose_name="Account Name", max_length=255)
    balance = models.FloatField(verbose_name="Balance")
    leverage = models.IntegerField(verbose_name="Leverage")
    percentage = models.FloatField(verbose_name="Percentage")

    def getSize(self):
        return self.balance * self.percentage * self.leverage


class PaperPositionModel(models.Model):
    paperAccount = models.ForeignKey(PaperAccountModel, verbose_name="Paper Account", on_delete=models.CASCADE)
    pair = models.ForeignKey('binanceAPI.PairModel', on_delete=models.CASCADE)
    size = models.FloatField(verbose_name="Size", blank=True, null=True)
    quantity = models.FloatField(verbose_name="Quantity", blank=True, null=True)

class PaperPositionLogModel(models.Model):
    paperPosition = models.ForeignKey(PaperPositionModel, verbose_name="Paper Position", on_delete=models.CASCADE)
    logDate = models.DateTimeField(verbose_name="Log Date", auto_now_add=True)
    logType = models.CharField(verbose_name="Log Type", max_length=255, choices=LOG_CHOICES)
    side = models.CharField(verbose_name="Side", max_length=255)
    price = models.FloatField(verbose_name="Price")
    size = models.FloatField(verbose_name="Size")
    profit = models.FloatField(verbose_name="Profit")
    commision = models.FloatField(verbose_name="Commision")
