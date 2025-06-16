from django.shortcuts import render
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from functools import wraps
from django.utils import timezone
from datetime import timedelta, datetime
from .models import Role, Right, RoleRight, CustomUser, Object, JobTitle, Employee, ClientsApplicationStatus, ClientsApplicationType, ClientsApplication, WorkTimeTracking, Material

# Проверка авторизации
def custom_login_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if 'user_id' not in request.session:
            return JsonResponse({'error': 'Not authenticated'}, status=401)
        try:
            request.user = CustomUser.objects.get(id=request.session['user_id'])
        except CustomUser.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=401)
        return view_func(request, *args, **kwargs)
    return _wrapped_view

# Выход из системы
def logout(request):
    if 'user_id' in request.session:
        del request.session['user_id']
        request.session.modified = True
    return JsonResponse({'status': 'Logged out'})

# Вход в систему (view)
class LoginAPIView(APIView):
    def post(self, request):
        login = request.data.get('login')
        password = request.data.get('password')

        try:
            user = CustomUser.objects.get(login=login)
            if user.check_password(password):
                request.session['user_id'] = user.id
                request.session.modified = True  # Принудительно сохраняем сессию
                return JsonResponse({'status': 'Success'})
            return Response({'error': 'Wrong password'}, status=status.HTTP_401_UNAUTHORIZED)
        except CustomUser.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_401_UNAUTHORIZED)

# Добавление нового пользователя
class RegistrationAPIView(APIView):
    """
    Регистрация нового пользователя
    """
    def post(self, request):
        serializer = CustomUserSerializer(data=request.data)
        
        if serializer.is_valid():
            # Дополнительные проверки перед созданием пользователя
            if CustomUser.objects.filter(login=serializer.validated_data['login']).exists():
                return Response(
                    {'error': 'Пользователь с таким логином уже существует'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Создаем пользователя через сериализатор
            user = serializer.save()
            
            # Возвращаем данные пользователя (без пароля)
            return Response({
                'id': user.id,
                'login': user.login,
                'role': user.role.name if user.role else None
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


##### ДЛЯ ТЕСТОВ #####
@custom_login_required
def protected_auth_check(request):
    user = request.user  # Уже будет доступен благодаря декоратору
    return JsonResponse({'status': 'authenticated', 'login': user.login})