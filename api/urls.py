from django.urls import path, include
from django.shortcuts import redirect
from rest_framework.routers import DefaultRouter

from .views import (
    # Импорт ViewSet
    UserViewSet, 
    EmployeeViewSet, 
    JobTitleViewSet, 
    ObjectViewSet,
    ClientsApplicationTypeViewSet,
    ClientsApplicationStatusViewSet,
    ClientsApplicationViewSet,
    MaterialViewSet,
    RoleViewSet,

    # Импорт логики WTT
    StartWorkAPIView,
    EndWorkAPIView,
    UpdateWorkTimeTrackingAPIView,
    DeleteWorkTimeTrackingAPIView,
    ListWorkTimeTrackingAPIView,

    # Импорт служебной логики
    LoginAPIView, 
    LogoutAPIView,
    CheckLoginAPIView,

    RenderPageAPIView
)

# Настройка роутера
router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'employees', EmployeeViewSet, basename='employee')
router.register(r'job-titles', JobTitleViewSet, basename='job-title')
router.register(r'objects', ObjectViewSet, basename='object')
router.register(r'application-types', ClientsApplicationTypeViewSet, basename='application-type')
router.register(r'application-statuses', ClientsApplicationStatusViewSet, basename='application-statuse')
router.register(r'applications', ClientsApplicationViewSet, basename='application')
router.register(r'materials', MaterialViewSet, basename='material')
router.register(r'roles', RoleViewSet, basename='role')

# URL паттерны
urlpatterns = [
    path('', lambda request: redirect('pages/index/', permanent=False)),

    path('pages/<str:page_name>/', RenderPageAPIView.as_view(), name='render_page_api'),

    # Роутер
    path('api/', include(router.urls)),

    # Служебное
    path('api/login/', LoginAPIView.as_view(), name='login'),
    path('api/logout/', LogoutAPIView.as_view(), name='logout'),
    path('api/check-login/', CheckLoginAPIView.as_view(), name='check-login'),
    
    # WTT
    path('api/wtt/start/', StartWorkAPIView.as_view()),
    path('api/wtt/stop/', EndWorkAPIView.as_view()),
    path('api/wtt/updateWTT/', UpdateWorkTimeTrackingAPIView.as_view()),
    path('api/wtt/deleteWTT/', DeleteWorkTimeTrackingAPIView.as_view()),
    path('api/wtt/listWTT/', ListWorkTimeTrackingAPIView.as_view()),
]