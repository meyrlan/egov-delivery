from django.urls import include, path
from core.views import *

urlpatterns = [
    path("document_info", DocumentOrderInfoView.as_view(), name="document_order"),
]
