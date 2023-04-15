from django.urls import include, path
from core.views import *
from core.views import *

urlpatterns = [
    path('document-order',
         DocumentOrderView.as_view()),
]
