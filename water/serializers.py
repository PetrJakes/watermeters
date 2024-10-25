# water/serializers.py
from rest_framework import serializers # type: ignore
from .models import Watermeter

class WatermeterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Watermeter
        fields = ['sn', 'recent_reading']
        #fields = ['sn', 'recent_reading', 'date_of_recent_reading']
