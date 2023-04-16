from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from core.views import *

router = DefaultRouter()
router.register('address', AddressViewSet)
router.register('users', UserViewSet)

urlpatterns = [
    path('user_by_iin', UserInfoByIIN.as_view()),
    path('coordinates_by_address', AddressCoordinateView.as_view()),
    path('courier_companies', CourierCompanies.as_view()),
    path('document_order',
         DocumentOrderView.as_view()),
    path('document_orders/<int:id>', DocumentOrderByCompanyList.as_view()),
    path('document_orders/my', DocumentOrderByCourierList.as_view()),
    path('document_orders', DocumentOrderList.as_view()),
    path('profile', ProfileView.as_view()),
    path("document_order/pick", DocumentOrderPickView.as_view()),
    path("document_order/drop", DocumentOrderDropView.as_view()),
    path("document_order/approve", DocumentOrderApproveView.as_view()),
    path("document_order/hand", DocumentOrderHandView.as_view()),
    path("document_order/update_coordinate",
         DocumentOrderUpdateCoordinate.as_view()),
    path("document_order/get_info/<str:request_id>",
         DocumentOrderGetCoordinate.as_view()),
    path("document_order/<str:request_id>",
         DocumentOrderUpdateView.as_view()),
    path("payment/webhook", PaymentWebhook.as_view()),
    path('token', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh', TokenRefreshView.as_view(), name='token_refresh'),
]

urlpatterns += router.urls
