from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import ListAPIView, UpdateAPIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from core.serializers import *
from core.models import *
from egov_delivery.external_api.egov import Client as EgovClient


class DocumentOrderView(APIView):
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


class CourierCompanyViewSet(ModelViewSet):
    queryset = CourierCompany.objects.all()
    serializer_class = CourierCompanySerializer


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class DocumentOrderList(ListAPIView):
    queryset = DocumentOrder.objects.all()
    serializer_class = DocumentOrderInfoSerializer

    def get_queryset(self):
        return DocumentOrder.objects.filter(status=DocumentOrder.STATUS.PAID,
                                            courier__courier_company__name=self.kwargs['courier_company'])


class DocumentOrderUpdate(UpdateAPIView):
    queryset = DocumentOrder.objects.all()
    serializer_class = DocumentOrderInfoSerializer
    permission_classes = [IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        courier = request.data.get('courier', None)

        if courier and not instance.courier and request.user.role == User.ROLE.COURIER:
            self.perform_update(serializer)
            return Response(serializer.data)

        return Response(
            status=status.HTTP_400_BAD_REQUEST,
            data={"message": }
        )
