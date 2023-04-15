from django.shortcuts import render
from rest_framework.generics import RetrieveAPIView


class DocumentOrderInfoView(RetrieveAPIView):
    serializer_class = DocumentOrderInfoSerializer

    def get_object(self):
        return self.request.user.driver
