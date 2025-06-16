from django.urls import path

from .views import LoginAPIView, protected_auth_check, logout

urlpatterns = [
    path('api/login/', LoginAPIView.as_view(), name='login'),
    path('api/logout/', logout, name='logout'),

    path('api/test/', protected_auth_check, name='test'),
]