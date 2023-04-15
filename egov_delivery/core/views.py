from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response

from core.serializers import *
from core.models import *
from egov_delivery.external_api.egov import Client as EgovClient


class DocumentOrderView(APIView):
    def post(self, request, format=None):
        request_id = request.data.get('request_id')
        iin = request.data.get('iin')

        try:
            client, _ = Client.objects.get_or_create(iin=iin)
        except Exception as e:
            print(e)
            return Response(
                status=status.HTTP_404_NOT_FOUND,
                data={"message": "Invalid IIN"}
            )

        document_response = EgovClient().get_document_order(
            request_id=request_id,
            iin=iin,
        )
        if document_response.status_code != 200:
            return Response(
                status=status.HTTP_404_NOT_FOUND,
                data={"message": "Invalid request ID"}
            )

        document_order, _ = DocumentOrder.objects.get_or_create(
            client=client,
            request_id=request_id,
        )

        serializer = DocumentOrderInfoSerializer(document_order)
        return Response(serializer.data, status=status.HTTP_200_OK)
