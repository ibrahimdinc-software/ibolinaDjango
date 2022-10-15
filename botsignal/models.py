from django.db import models

# Create your models here.

class SignalModel(models.Model):
    time = models.DateTimeField(verbose_name="Date", auto_now_add=True, blank=True, null=True)
    pair = models.CharField("Pair", max_length=255)
    side = models.CharField("Side", max_length=255)
    entryOne = models.FloatField("Entry 1")
    entryTwo = models.FloatField("Entry 2")
    stoploss = models.FloatField("Stoploss")
    isOpen = models.BooleanField("Is Open", default=True, blank=True, null=True)
    
    def __str__(self) -> str:
        return self.pair

class SignalTargetsModel(models.Model):
    signal = models.ForeignKey(SignalModel, related_name="signal_model", on_delete=models.CASCADE)
    name = models.CharField(verbose_name="Target Name", max_length=255)
    price = models.FloatField(verbose_name="Target Price")


