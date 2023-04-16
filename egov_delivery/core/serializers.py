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
    trusted_client = ClientInfoSerializer()
    courier = CourierInfoSerializer()
    delivery_address = AddressSerializer()

    class Meta:
        model = DocumentOrder
        fields = ["request_id", "client", "trusted_client",
                  "courier", "delivery_address", "status", "service_name", "delivery_datetime"]


class DocumentOrderUpdateSerializer(serializers.ModelSerializer):
    courier_company_id = serializers.PrimaryKeyRelatedField(
        queryset=CourierCompany.objects.all(),
        source="courier_company",
        write_only=True,
        many=False,
    )
    delivery_address = AddressSerializer()

    class Meta:
        model = DocumentOrder
        fields = ["request_id", "delivery_address",
                  "delivery_datetime", "courier_company_id"]


class UserSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        user = super().create(validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user

    def update(self, instance, validated_data):
        if validated_data.get('password'):
            instance.password = instance.set_password(
                validated_data['password'])
        instance.save()
        return instance

    class Meta:
        model = User
        fields = "__all__"
