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
        model = User
        fields = [
            "phone_number",
        ]


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = "__all__"


class DocumentOrderInfoSerializer(serializers.ModelSerializer):
    client = ClientInfoSerializer()
    courier = CourierInfoSerializer()
    delivery_address = AddressSerializer()

    class Meta:
        model = DocumentOrder
        fields = ["request_id", "client",
                  "courier", "delivery_address", "status", "service_name", "delivery_datetime"]


class CourierCompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = CourierCompany
        fields = "__all__"


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"
