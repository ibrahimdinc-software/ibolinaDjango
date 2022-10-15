"""

from rest_framework import serializers
from binanceAPI.module import SignalToOrder

from .models import SignalModel, SignalTargetsModel
class SignalTargetsModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = SignalTargetsModel
        fields = ['name', 'price']

class SignalModelSerializer(serializers.ModelSerializer):
    targets = SignalTargetsModelSerializer(source="signal_model",many=True)
    class Meta:
        model = SignalModel
        fields = ['pair', 'side', 'entryOne', 'entryTwo', 'stoploss', 'targets']

    def create(self, validated_data):
        target = validated_data.pop('signal_model')
        newSignal = SignalModel.objects.create(**validated_data)
        for i in target:
            SignalTargetsModel.objects.create(**i, signal=newSignal)
        
        sto = SignalToOrder()
        print(newSignal.pair)
        sto.createOrders(newSignal)

        return newSignal
"""