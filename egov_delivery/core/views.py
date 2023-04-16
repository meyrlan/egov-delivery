import json
from decimal import Decimal
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import ListAPIView, RetrieveAPIView, UpdateAPIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from core.utils import get_random_code, get_route_payment_amount
from rest_framework.exceptions import NotFound
from django.conf import settings

from core.serializers import *
from core.models import *
from egov_delivery.external_api.egov import Client as EgovClient

import stripe
import datetime

PAYMENT_EVENT_TYPES = ["payment_intent.created",
                       "charge.succeeded", "charge.failed"]


class IsCourierPermission(IsAuthenticated):
    def has_permission(self, request, view):
        return super().has_permission(request, view) and request.user.role == User.ROLE.COURIER


class CourierCompanies(APIView):
    permission_classes = [AllowAny]

    def get(self, request, format=None):
        request_id = request.GET.get("request_id")
        document_order = DocumentOrder.objects.filter(
            request_id=request_id).first()

        if not document_order:
            return Response(
                status=status.HTTP_404_NOT_FOUND,
                data={
                    "message": f"Document Order with request ID {request_id} not found."}
            )

        payment_amount = get_route_payment_amount(
            document_order.delivery_address,
            document_order.service_center.address
        )
        companies = []
        for company in CourierCompany.objects.all():
            companies.append({
                "id": company.id,
                "name": company.name,
                "price": float(float(company.price_coefficient) * float(payment_amount)),
            })

        print(companies)

        return Response(
            status=status.HTTP_200_OK,
            data={"companies": companies}
        )


class PaymentWebhook(APIView):
    permission_classes = [AllowAny]

    def post(self, request, format=None):
        print(request.data)
        event_dict = request.data

        intent = event_dict.get("data", {}).get("object")
        request_id = intent.get("metadata", {}).get("request_id")
        document_order = DocumentOrder.objects.filter(
            request_id=request_id).first()

        if not document_order:
            return Response(
                status=status.HTTP_404_NOT_FOUND,
                data={"message": "Document order not found"}
            )

        if document_order.status > DocumentOrder.STATUS.READY:
            return Response(
                status=status.HTTP_200_OK,
                data={"message": "Paid document order"}
            )

        if event_dict["type"] not in PAYMENT_EVENT_TYPES:
            return Response(
                status=status.HTTP_200_OK,
                data={"message": "Unknown events"}
            )

        if event_dict["type"] == "payment_intent.created":
            print(f"Payment created for {document_order}")

        if event_dict["type"] == "charge.succeeded":
            document_order.status = DocumentOrder.STATUS.PAID

        document_order.save()
        return Response(
            status=status.HTTP_200_OK,
            data={"message": "OK"}
        )


class DocumentOrderView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, format=None):
        request_id = request.data.get('request_id')
        iin = request.data.get('iin')

        try:
            client, _ = Client.objects.get_or_create(iin=iin)
        except:
            return Response(
                status=status.HTTP_404_NOT_FOUND,
                data={"message": "Invalid IIN"}
            )

        document_response = EgovClient().get_document_order(
            request_id=request_id,
            iin=iin,
        )
        document_json = document_response.json()
        if document_response.status_code != 200 or document_json.get("data", {}).get("resultCode") != "OK":
            return Response(
                status=status.HTTP_404_NOT_FOUND,
                data={"message": "Invalid request ID"}
            )

        try:
            document_order, _ = DocumentOrder.objects.get_or_create(
                client=client,
                request_id=request_id,
                service_center=ServiceCenter.objects.first(),
                service_name=document_json.get("data", {}).get(
                    "serviceType", {}).get("nameRu", "Неизвестно"),
            )
        except Exception as e:
            print(e)
            return Response(
                status=status.HTTP_404_NOT_FOUND,
                data={"message": e}
            )

        serializer = DocumentOrderInfoSerializer(document_order)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AddressViewSet(ModelViewSet):
    queryset = Address.objects.all()
    serializer_class = AddressSerializer
    permission_classes = [AllowAny]


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]


class UserInfoByIIN(APIView):
    def post(self, request, format=None):
        iin = request.data.get('iin')

        response = EgovClient().get_user_by_iin(iin)

        if response.status_code != 200:
            return Response(
                status=status.HTTP_404_NOT_FOUND,
                data={"message": "Invalid IIN"}
            )

        user_info = response.json()

        response = EgovClient().get_phone_number_by_iin(iin)

        response_json = response.json()
        if response.status_code == 200 and response_json.get("isExists"):
            user_info["phone"] = response_json.get("phone")

        return Response(
            status=status.HTTP_200_OK,
            data=user_info,
        )


class AddressCoordinateView(APIView):
    def post(self, request, format=None):
        address = request.data.get('address')

        try:
            address = get_address_lat_lng(address)
        except:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={"message": "Couldn't find coordinates"}
            )

        return Response(
            status=status.HTTP_200_OK,
            data=address
        )


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)


class DocumentOrderByCompanyList(ListAPIView):
    queryset = DocumentOrder.objects.all()
    serializer_class = DocumentOrderInfoSerializer

    def get_queryset(self):
        return DocumentOrder.objects.filter(status=DocumentOrder.STATUS.PAID,
                                            courier_company__id=self.kwargs['id'])


class DocumentOrderByCourierList(ListAPIView):
    queryset = DocumentOrder.objects.all()
    serializer_class = DocumentOrderInfoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return DocumentOrder.objects.filter(courier=self.request.user)


class DocumentOrderRetrieveView(RetrieveAPIView):
    queryset = DocumentOrder.objects.all()
    serializer_class = DocumentOrderInfoSerializer
    lookup_field = "request_id"


class DocumentOrderUpdateView(UpdateAPIView):
    queryset = DocumentOrder.objects.all()
    serializer_class = DocumentOrderUpdateSerializer
    lookup_field = "request_id"

    def patch(self, request, *args, **kwargs):
        request_id = kwargs.get('request_id')
        is_cashback_used = kwargs.get('is_cashback_used')
        document_order = DocumentOrder.objects.filter(
            request_id=request_id).first()

        if not document_order:
            return Response(
                status=status.HTTP_404_NOT_FOUND,
                data={"message": "Invalid request ID"}
            )

        trusted_client_iin = request.data.get("trusted_client_iin")
        if trusted_client_iin:
            try:
                client, _ = Client.objects.get_or_create(
                    iin=request.data.get("trusted_client_iin"))
            except:
                raise ValidationError("Invalid trusted client IIN")
            document_order.trusted_client = client
            document_order.save()

        stripe.api_key = settings.STRIPE_SECRET_KEY
        amount = get_route_payment_amount(
            document_order.delivery_address,
            document_order.service_center.address,
        )

        print(amount)

        if is_cashback_used == True:
            amount -= document_order.client.cashback
        elif is_cashback_used == False:
            document_order.client.cashback += Decimal(float(amount) * 0.05)
            document_order.client.save()

        print(amount)

        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    "price_data": {
                        "product_data": {
                            "name": f"Доставка документа: {document_order.service_name}",
                        },
                        "currency": "kzt",
                        "unit_amount": int(amount * 100),
                    },
                    "quantity": 1,
                },
            ],
            payment_intent_data={
                "metadata": {
                    "request_id": document_order.request_id,
                },
            },
            mode="payment",
            success_url=f"{settings.FRONTEND_URL}/ordered?request_id={request_id}&iin={document_order.client.iin}",
            cancel_url=f"{settings.FRONTEND_URL}/ordered?request_id={request_id}&iin={document_order.client.iin}",
        )
        # document_order.status = DocumentOrder.STATUS.PAID
        # document_order.save() # Uncomment if stripe doesn't work
        self.partial_update(request, *args, **kwargs)
        return Response(
            status=status.HTTP_200_OK,
            data={"url": checkout_session.url}
        )


class DocumentOrderList(ListAPIView):
    queryset = DocumentOrder.objects.all()
    serializer_class = DocumentOrderInfoSerializer

    def get_queryset(self):
        return DocumentOrder.objects.exclude(status__in=[DocumentOrder.STATUS.READY, DocumentOrder.STATUS.HANDED])


class DocumentOrderPickView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        request_id = request.data.get('request_id')

        try:
            document_order = DocumentOrder.objects.get(request_id=request_id)
        except:
            return Response(
                status=status.HTTP_404_NOT_FOUND,
                data={"message": "Invalid order_id"}
            )

        if document_order.courier:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={"message": "This order already has assigned courier"}
            )

        print(request.user)

        if request.user.role != User.ROLE.COURIER:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={"message": "You are not a courier"}
            )

        document_order.courier = request.user
        document_order.status = DocumentOrder.STATUS.COURIER_ASSIGNED
        document_order.courier_code = get_random_code(4)
        document_order.save()

        if document_order.trusted_client:
            EgovClient().send_message_by_phone_number(str(document_order.trusted_client.phone_number),
                                                      f"На ваш заказ с номером {document_order.request_id} назначен курьер {document_order.courier.full_name}. Время назначения курьера {datetime.datetime.now().strftime('%Y/%m/%d %H:%M')}")
        else:
            EgovClient().send_message_by_phone_number(str(document_order.client.phone_number),
                                                      f"На ваш заказ с номером {document_order.request_id} назначен курьер {document_order.courier.full_name}. Время назначения курьера {datetime.datetime.now().strftime('%Y/%m/%d %H:%M')}")

        EgovClient().send_message_by_phone_number(str(document_order.courier.phone_number),
                                                  f"Заказ с номером {document_order.request_id} готов для выдачи по адресу {document_order.service_center.name} ({document_order.service_center.address.street} {document_order.service_center.address.house_number}). Сообщите этот код оператору: {document_order.courier_code}")

        return Response(
            status=status.HTTP_200_OK,
            data={"message": f"You are assigned as a courier to the order with request_id: {document_order.request_id}"}
        )


class DocumentOrderDropView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        request_id = request.data.get('request_id')

        try:
            document_order = DocumentOrder.objects.get(request_id=request_id)
        except:
            return Response(
                status=status.HTTP_404_NOT_FOUND,
                data={"message": "Invalid request id"}
            )

        if document_order.courier != request.user:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={"message": "You are not the assigned courier for this order"}
            )

        if document_order.status != DocumentOrder.STATUS.COURIER_ASSIGNED:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={
                    "message": f"You can not drop the order with status: {document_order.status}"}
            )

        document_order.courier = None
        document_order.status = DocumentOrder.STATUS.PAID
        document_order.courier_code = None
        document_order.save()

        return Response(
            status=status.HTTP_200_OK,
            data={
                "message": f"You are successfully dropped order with request_id: {document_order.request_id}"}
        )


class DocumentOrderApproveView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        courier_code = request.data.get('courier_code')
        request_id = request.data.get('request_id')

        try:
            document_order = DocumentOrder.objects.get(request_id=request_id)
        except:
            return Response(
                status=status.HTTP_404_NOT_FOUND,
                data={"message": "Invalid request id"}
            )

        if document_order.status != DocumentOrder.STATUS.COURIER_ASSIGNED:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={
                    "message": f"The status of the order not equal to {DocumentOrder.STATUS.COURIER_ASSIGNED}"}
            )

        if document_order.courier_code != courier_code:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={"message": "Invalid courier code"}
            )

        document_order.status = DocumentOrder.STATUS.COURIER_ON_THE_WAY
        document_order.client_code = get_random_code(4)
        document_order.save()

        if document_order.trusted_client:
            EgovClient().send_message_by_phone_number(str(document_order.trusted_client.phone_number),
                                                      f"Заказ с номером {document_order.request_id} будет доставлен в {document_order.delivery_datetime.strftime('%Y/%m/%d %H:%M')}. Сообщите этот код курьеру: {document_order.client_code}")
        else:
            EgovClient().send_message_by_phone_number(str(document_order.client.phone_number),
                                                      f"Заказ с номером {document_order.request_id} будет доставлен в {document_order.delivery_datetime.strftime('%Y/%m/%d %H:%M')}. Сообщите этот код курьеру: {document_order.client_code}")

        return Response(
            status=status.HTTP_200_OK,
            data={"message": "OK"}
        )


class DocumentOrderHandView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        client_code = request.data.get('client_code')
        request_id = request.data.get('request_id')

        try:
            document_order = DocumentOrder.objects.get(request_id=request_id)
        except:
            return Response(
                status=status.HTTP_404_NOT_FOUND,
                data={"message": "Invalid request id"}
            )

        if document_order.status != DocumentOrder.STATUS.COURIER_ON_THE_WAY:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={
                    "message": f"The status of the order not equal to {DocumentOrder.STATUS.COURIER_ASSIGNED}"}
            )

        if document_order.client_code != client_code:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={"message": "Invalid client code"}
            )

        document_order.status = DocumentOrder.STATUS.HANDED
        document_order.save()

        return Response(
            status=status.HTTP_200_OK,
            data={"message": "OK"}
        )


class DocumentOrderUpdateCoordinate(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        request_id = request.data.get('request_id')
        lat = request.data.get('lat')
        lng = request.data.get('lng')

        try:
            document_order = DocumentOrder.objects.get(request_id=request_id)
        except:
            return Response(
                status=status.HTTP_404_NOT_FOUND,
                data={"message": "Invalid request id"}
            )

        if document_order.courier != request.user:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={"message": "You are not the courier assigned to this order"}
            )

        document_order.lat = lat
        document_order.lng = lng
        document_order.save()

        return Response(
            status=status.HTTP_200_OK,
            data={"message": "OK"}
        )


class DocumentOrderGetCoordinate(RetrieveAPIView):
    queryset = DocumentOrder.objects.all()
    serializer_class = DocumentOrderInfoSerializer
    lookup_field = "request_id"
