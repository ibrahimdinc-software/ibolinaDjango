from django.db import models
# Create your models here.

SIDE_CHOICES = (
    ('short', 'SHORT'),
    ('long', 'LONG'),
)

INTERVAL_CHOISES = (
    ('15m','15m'),
    ('30m','30m'),
    ('1h','1h'),
    ('2h','2h'),
    ('4h','4h'),
    ('1d','1d'),
)

class BinanceApiModel(models.Model):
    user = models.ForeignKey("auth.user", on_delete=models.CASCADE)
    name = models.CharField("Account Name", max_length=255)
    apiKey = models.CharField("API Key", max_length=255)
    apiSecretKey = models.CharField("API Secret Key", max_length=255)
    isActive = models.BooleanField('Is Active?')
    hedgeMode = models.BooleanField('Hedge Mode')

    def __str__(self) -> str:
        return self.name


class PairModel(models.Model):
    pair = models.CharField(verbose_name="Pair", max_length=255)
    interval = models.CharField(verbose_name="Interval", choices=INTERVAL_CHOISES, max_length=255)
    pMaxLen = models.IntegerField(verbose_name="PMax Length")
    pMaxMultiplier = models.FloatField(verbose_name="PMax Multiplier Length")
    emaLen = models.IntegerField(verbose_name="EMA Length")
    hmaLen = models.IntegerField(verbose_name="HullMA Length")
    rrRatio = models.FloatField(verbose_name='Risk/Reward Ratio')
    trailingClose = models.BooleanField(verbose_name="Use Trailing Close")
    inPos = models.CharField(verbose_name="In Position", max_length=255, blank=True, null=True, default="NONE")
    entryPrice = models.FloatField(verbose_name="Entry Price", blank=True, null=True)
    tpPrice = models.FloatField(verbose_name="Take Profit Price", blank=True, null=True)
    stopPrice = models.FloatField(verbose_name="Stop Price", blank=True, null=True)
    cooldownDate = models.DateTimeField(verbose_name='Cooldown Date', blank=True, null=True)

    def __str__(self) -> str:
        return self.pair

    def getDatas(self):
        from techAnalys.module import IndicatorCalculatorModule
        icm = IndicatorCalculatorModule(self.pair, self.pMaxLen, self.pMaxMultiplier, self.emaLen, self.hmaLen, self.interval)
        datas = icm.calcIndicators()

        for i, row in datas.iterrows():
            KlineIndicatorModel.objects.get_or_create(
                pair = self,
                openTime=row['Open Time'], 
                closeTime=row['Close Time'],
                open = row['Open'],
                high = row['High'],
                low = row['Low'],
                close = row['Close'],
                var = row['var'],
                pmax = row['pmax'],
                hma = row['hma'],
            )


class PairTpModel(models.Model):
    pair = models.ForeignKey(PairModel, on_delete=models.CASCADE)
    tpRate = models.FloatField(verbose_name='TP Ratio')
    tpPrice = models.FloatField(verbose_name='TP Price', blank=True, null=True)
    isTaken = models.BooleanField(verbose_name='Is TP Taken?', default=False)


class PairPosModel(models.Model):
    pair = models.ForeignKey(PairModel, on_delete=models.CASCADE)
    bam = models.ForeignKey(BinanceApiModel, on_delete=models.CASCADE)
    quantity = models.FloatField(verbose_name="Quantity", blank=True, null=True)

class KlineIndicatorModel(models.Model):
    pair = models.ForeignKey(PairModel, on_delete=models.CASCADE)
    openTime = models.DateTimeField(verbose_name="Open Time")
    closeTime = models.DateTimeField(verbose_name="Close Time")
    open = models.FloatField(verbose_name="Open")
    high = models.FloatField(verbose_name="High")
    low = models.FloatField(verbose_name="Low")
    close = models.FloatField(verbose_name="Close")

    var = models.FloatField(verbose_name="VAR")
    pmax = models.FloatField(verbose_name="PMax")
    hma = models.FloatField(verbose_name="HullMA")

    def __str__(self) -> str:
        return str(self.pair)


class StrategyModel(models.Model):
    bam = models.ForeignKey(BinanceApiModel, on_delete=models.CASCADE)
    pair = models.ForeignKey(PairModel, on_delete=models.CASCADE)
    interval = models.CharField(verbose_name="Interval", choices=INTERVAL_CHOISES, max_length=255)
    bigDonLen = models.IntegerField(verbose_name="Big Don Len")
    smallDonLen = models.IntegerField(verbose_name="Small Don Len")
    emaLen = models.IntegerField(verbose_name="EMA Len")
    trailingClose = models.BooleanField(verbose_name="Use Trailing Close")
    firstTPrrRatio = models.FloatField(verbose_name="First TP Risk/Reward Ratio")
    firstTPclosePrecentage = models.IntegerField(verbose_name="First TP Closing Percentage")
    rrRatio = models.FloatField(verbose_name="Risk/Reward Ratio")
    def __str__(self) -> str:
        return str(self.pair)
