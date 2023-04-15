from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from core.views import *

router = DefaultRouter()
router.register('address', AddressViewSet)
router.register('courier_company', CourierCompanyViewSet)

urlpatterns = [
    path('document-order',
         DocumentOrderView.as_view()),
    path('paid_orders', DocumentOrderList.as_view()),
    path('token', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh', TokenRefreshView.as_view(), name='token_refresh'),
]

urlpatterns += router.urls
