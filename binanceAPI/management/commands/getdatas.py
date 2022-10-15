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
        pms = PairModel.objects.all()
        for pm in pms:
            pm.getDatas()
        



