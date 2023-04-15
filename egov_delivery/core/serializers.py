from rest_framework import serializers
from core.models import *


class ClientInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = [
            "firstname",
            "middlename",
            "lastname",
            "iin",
            "home_address",
            "cashback",
            "phone_number",
        ]


class CourierInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Courier
        fields = [
            "phone_number",
        ]


class DocumentOrderInfoSerializer(serializers.ModelSerializer):
    client = ClientInfoSerializer()
    courier = CourierInfoSerializer()

    class Meta:
        model = DocumentOrder
        fields = ["request_id", "client", "courier", "status"]
