from django.shortcuts import render
from django.http import JsonResponse
from django.http import HttpResponseForbidden, HttpResponseNotFound
from django.core.exceptions import ValidationError

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
from rest_framework import viewsets, status
from rest_framework.permissions import BasePermission

from datetime import date, datetime

from .models import (
    CustomUser, 
    Employee,
    JobTitle,
    Object,
    Material,
    ClientsApplicationType,
    ClientsApplicationStatus, 
    ClientsApplication, 
    WorkTimeTracking,
    Role
)

from .serializers import (
    CustomUserSerializer,
    EmployeeSerializer,
    JobTitleSerializer,
    ObjectSerializer, 
    MaterialSerializer,
    ClientsApplicationTypeSerializer, 
    ClientsApplicationStatusSerializer,
    ClientsApplicationSerializer, 
    StartWorkSerializer, 
    EndWorkSerializer,
    WorkTimeTrackingSerializer,
    RoleSerializer,
)

##### FRONTEND #####

# Конфигурация страниц: шаблон + роли (None = открытая страница)
PAGE_CONFIG = {
    'index': {
        'template': 'index.html',
        'auth_required': False,  # не требует авторизации
    },
    'auth': {
        'template': 'auth.html',
        'auth_required': False,
        #'roles': ['admin', 'hr', 'basic'],
    },
    'clientsApplications': {
        'template': 'clientsApplications.html',
        'auth_required': False,
        #'roles': ['admin', 'hr', 'basic'],
    },
    'clientsApplicationsStatuses': {
        'template': 'clientsApplicationsStatuses.html',
        'auth_required': False,
        #'roles': ['admin', 'hr', 'basic'],
    },
    'clientsApplicationsTypes': {
        'template': 'clientsApplicationsTypes.html',
        'auth_required': False,
        #'roles': ['admin', 'hr', 'basic'],
    },
    'dashboard': {
        'template': 'dashboard.html',
        'auth_required': False,
        #'roles': ['admin', 'hr', 'basic'],
    },
    'employeers': {
        'template': 'employeers.html',
        'auth_required': False,
        #'roles': ['admin', 'hr', 'basic'],
    },
    'materials': {
        'template': 'materials.html',
        'auth_required': False,
        #'roles': ['admin', 'hr', 'basic'],
    },
    'objects': {
        'template': 'objects.html',
        'auth_required': False,
        #'roles': ['admin', 'hr', 'basic'],
    },
    'roles': {
        'template': 'roles.html',
        'auth_required': False,
        #'roles': ['admin', 'hr', 'basic'],
    },
    'timeTracker': {
        'template': 'timeTracker.html',
        'auth_required': False,
        #'roles': ['admin', 'hr', 'basic'],
    },
    'users': {
        'template': 'users.html',
        'auth_required': False,
        #'roles': ['admin', 'hr', 'basic'],
    },
    'jobTitles': {
        'template': 'jobTitles.html',
        'auth_required': False,
        #'roles': ['admin', 'hr', 'basic'],
    },
}

# Рендер страниц
class RenderPageAPIView(APIView):
    permission_classes = []  # динамически назначаются

    def get_permissions(self):
        page_name = self.kwargs.get('page_name')
        config = PAGE_CONFIG.get(page_name)

        if not config:
            return [AllowAny()]  # Страница не найдена — пусть get обработает

        if not config.get('auth_required', False):
            return [AllowAny()]  # Страница доступна без авторизации

        # Если авторизация требуется — проверяем и роль (если указана)
        permissions = [IsSessionAuthenticated()]
        if 'roles' in config:
            permissions.append(roleRequiredPermissionFactory(config['roles'])())
        return permissions

    def get(self, request, page_name):
        config = PAGE_CONFIG.get(page_name)
        if not config:
            return HttpResponseNotFound("Page not found")

        return render(request, config['template'])



##### BACKEND #####

### СЛУЖЕБНОЕ ###

# Проверка активности сессии
class IsSessionAuthenticated(BasePermission):
    message = 'Not authenticated'

    def has_permission(self, request, view):
        user_id = request.session.get('user_id')
        if not user_id:
            return False
        try:
            request.my_user = CustomUser.objects.get(id=user_id)
            return True
        except CustomUser.DoesNotExist:
            return False

# Ответ о логине для фронта
class CheckLoginAPIView(APIView):
    permission_classes = [IsSessionAuthenticated]  # Используем ваш кастомный пермишен

    def get(self, request):
        # Если пермишен прошел, значит пользователь аутентифицирован
        return Response({'logged_in': True})


# Проверка доступа по роли
def roleRequiredPermissionFactory(allowed_roles):
    class CustomRolePermission(BasePermission):
        def has_permission(self, request, view):
            user = request.my_user
            if not user or not hasattr(user, 'role') or user.role is None:
                return False
            return user.role.name in allowed_roles
    return CustomRolePermission

# Вход в систему
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

# Выход из системы
class LogoutAPIView(APIView):
    permission_classes = [IsSessionAuthenticated]

    def post(self, request):
        if 'user_id' in request.session:
            del request.session['user_id']
            request.session.modified = True
        return Response({'status': 'Logged out'}, status=status.HTTP_200_OK)


### ПОЛЬЗОВАТЕЛИ ###
class UserViewSet(viewsets.ModelViewSet):
    permission_classes = [IsSessionAuthenticated, roleRequiredPermissionFactory(['admin'])]
    
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer

    # Создание нового пользователя
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        login = serializer.validated_data['login']
        if CustomUser.objects.filter(login=login).exists():
            return Response({'error': 'Пользователь с таким логином уже существует'}, status=status.HTTP_400_BAD_REQUEST)

        user = serializer.save()
        return Response({
            'id': user.id,
            'login': user.login,
            'role': user.role.name
        }, status=status.HTTP_201_CREATED)

    # Изменение пользователя
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        validated_data = serializer.validated_data

        if 'role' in validated_data:
            try:
                role = Role.objects.get(name=validated_data.pop('role'))
                instance.role = role
            except Role.DoesNotExist:
                return Response({'error': 'Роль с таким названием не существует'}, status=status.HTTP_400_BAD_REQUEST)

        if 'password' in validated_data:
            instance.password = validated_data.pop('password')

        serializer.update(instance, validated_data)
        instance.save()
        return Response({'message': 'Пользователь успешно обновлён'})

    # Удаление пользователя
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if hasattr(instance, 'employee') and instance.employee is not None:
            return Response({'error': 'Невозможно удалить пользователя, он привязан к сотруднику'}, status=status.HTTP_400_BAD_REQUEST)
        self.perform_destroy(instance)
        return Response({'message': 'Пользователь успешно удалён'}, status=status.HTTP_204_NO_CONTENT)


### СОТРУДНИКИ ###

class EmployeeViewSet(viewsets.ModelViewSet):
    permission_classes = [IsSessionAuthenticated, roleRequiredPermissionFactory(['admin', 'hr'])]

    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer

    # Создание нового сотрудника
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            employee = serializer.save()
            return Response({
                'message': 'Сотрудник успешно создан',
                'employee': {
                    'id': employee.id,
                    'fullName': employee.fullName,
                    'personnelNumber': employee.personnelNumber
                }
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Изменение сотрудника
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        try:
            employee = self.get_object()
        except Employee.DoesNotExist:
            return Response({'error': 'Сотрудник не найден'}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(employee, data=request.data, partial=partial)
        if serializer.is_valid():
            validated_data = serializer.validated_data

            # Обновляем только то, что пришло
            if 'jobTitle' in request.data:
                job_title = serializer.validate_jobTitle(request.data.get('jobTitle'))
                employee.jobTitle = job_title

            if 'object' in request.data:
                obj = serializer.validate_object(request.data.get('object'))
                employee.object = obj

            if 'user' in request.data:
                user = serializer.validate_user(request.data.get('user'))
                employee.user = user

            # Обновление остальных полей
            serializer.update(employee, validated_data)
            employee.save()

            return Response({'message': 'Сотрудник успешно обновлён'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Удаление сотрудника
    def destroy(self, request, *args, **kwargs):
        try:
            employee = self.get_object()
            employee.delete()
            return Response({'message': 'Сотрудник успешно удалён'}, status=status.HTTP_204_NO_CONTENT)
        except Employee.DoesNotExist:
            return Response({'error': 'Сотрудник не найден'}, status=status.HTTP_404_NOT_FOUND)


### ДОЛЖНОСТИ ###

class JobTitleViewSet(viewsets.ModelViewSet):
    permission_classes = [IsSessionAuthenticated, roleRequiredPermissionFactory(['admin', 'hr'])]

    queryset = JobTitle.objects.all()
    serializer_class = JobTitleSerializer

    # Создание новой должности
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            job = serializer.save()
            return Response({'message': 'Должность успешно создана', 'id': job.id}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Изменение должности
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Должность успешно обновлена'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Удаление должности
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response({'message': 'Должность успешно удалена'}, status=status.HTTP_204_NO_CONTENT)


### ОБЪЕКТЫ ###

class ObjectViewSet(viewsets.ModelViewSet):
    permission_classes = [IsSessionAuthenticated, roleRequiredPermissionFactory(['admin', 'foreman'])]

    queryset = Object.objects.all()
    serializer_class = ObjectSerializer

    # Создание нового объекта
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            obj = serializer.save()
            return Response({'message': 'Объект успешно создан', 'id': obj.id}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Изменение объекта
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Объект успешно обновлён'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Удаление объекта
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response({'message': 'Объект успешно удалён'}, status=status.HTTP_204_NO_CONTENT)


### МАТЕРИАЛЫ ###

class MaterialViewSet(viewsets.ModelViewSet):
    permission_classes = [IsSessionAuthenticated, roleRequiredPermissionFactory(['admin', 'storekeeper'])]
    
    queryset = Material.objects.all()
    serializer_class = MaterialSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        material = serializer.save()
        return Response({
            'message': 'Материал успешно добавлен',
            'id': material.id
        }, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True  # разрешаем частичное обновление
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({'message': 'Материал успешно удалён'}, status=status.HTTP_204_NO_CONTENT)


### ЗАЯВКИ ###

# Типы заявок
class ClientsApplicationTypeViewSet(viewsets.ModelViewSet):
    permission_classes = [IsSessionAuthenticated, roleRequiredPermissionFactory(['admin'])]

    queryset = ClientsApplicationType.objects.all()
    serializer_class = ClientsApplicationTypeSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Тип успешно добавлен'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        partial = request.method == 'PATCH'
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Тип успешно обновлён'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response({'message': 'Тип удалён'})
       
# Статусы заявок
class ClientsApplicationStatusViewSet(viewsets.ModelViewSet):
    permission_classes = [IsSessionAuthenticated, roleRequiredPermissionFactory(['admin'])]

    queryset = ClientsApplicationStatus.objects.all()
    serializer_class = ClientsApplicationStatusSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Статус успешно добавлен'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        partial = request.method == 'PATCH'
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Статус успешно обновлён'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response({'message': 'Статус удалён'})

# Заявки
class ClientsApplicationViewSet(viewsets.ModelViewSet):
    permission_classes = [IsSessionAuthenticated, roleRequiredPermissionFactory(['admin', 'marketer'])]

    queryset = ClientsApplication.objects.all()
    serializer_class = ClientsApplicationSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            # Создание заявки доступно всем
            return [AllowAny()]
        # Остальные действия — только для авторизованных с ролями
        return [IsSessionAuthenticated(), roleRequiredPermissionFactory(['admin', 'marketer'])()]
    
    def perform_create(self, serializer):
        # Если клиент не передал явно тип и статус — ставим значения по умолчанию
        if not self.request.data.get('type_name'):
            try:
                type_obj = ClientsApplicationType.objects.get(name='Обратный звонок')
                serializer.validated_data['type'] = type_obj
            except ClientsApplicationType.DoesNotExist:
                raise ValidationError({'type': 'Тип "Обратный звонок" не найден'})

        if not self.request.data.get('status_name'):
            try:
                status_obj = ClientsApplicationStatus.objects.get(name='Новая')
                serializer.validated_data['status'] = status_obj
            except:
                raise ValidationError({'status': 'Статус "Новая" не найден'})
        
        serializer.save()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response({'message': 'Заявка успешно создана'}, status=status.HTTP_201_CREATED)


    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Заявка успешно обновлена'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response({'message': 'Заявка удалена'})


### WTT ###

# Отметка о начале работы
class StartWorkAPIView(APIView):
    permission_classes = [
        IsSessionAuthenticated, 
        roleRequiredPermissionFactory([
            'admin', 'hr', 'marketer',
            'foreman', 'storekeeper', 'basic'
        ])
    ]

    def post(self, request):
        serializer = StartWorkSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        employee = serializer.validated_data['personnelNumber']
        today = date.today()

        if WorkTimeTracking.objects.filter(employee=employee, date=today).exists():
            return Response({'error': 'Рабочий день уже начат'}, status=400)

        WorkTimeTracking.objects.create(
            employee=employee,
            date=today,
            startTime=datetime.now().time()
        )

        return Response({'message': 'Начало рабочего дня зафиксировано'}, status=201)

# Отметка о конце работы
class EndWorkAPIView(APIView):
    permission_classes = [
        IsSessionAuthenticated, 
        roleRequiredPermissionFactory([
            'admin', 'hr', 'marketer',
            'foreman', 'storekeeper', 'basic'
        ])
    ]

    def post(self, request):
        serializer = EndWorkSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        employee = serializer.validated_data['personnelNumber']
        today = date.today()

        try:
            tracking = WorkTimeTracking.objects.get(employee=employee, date=today)
        except WorkTimeTracking.DoesNotExist:
            return Response({'error': 'Сначала отметьте начало рабочего дня'}, status=400)

        if tracking.endTime:
            return Response({'error': 'Рабочий день уже завершён'}, status=400)

        tracking.endTime = datetime.now().time()
        tracking.save()

        return Response({'message': 'Конец рабочего дня зафиксирован'}, status=200)

# Обновление времени начала и/или конца рабочего дня сотрудника за сегодня
class UpdateWorkTimeTrackingAPIView(APIView):
    permission_classes = [IsSessionAuthenticated, roleRequiredPermissionFactory(['admin'])]

    def put(self, request):
        personnel_number = request.data.get('personnelNumber')
        if not personnel_number:
            return Response({'error': 'personnelNumber обязателен'}, status=400)

        try:
            employee = Employee.objects.get(personnelNumber=personnel_number)
        except Employee.DoesNotExist:
            return Response({'error': 'Сотрудник не найден'}, status=404)

        try:
            tracking = WorkTimeTracking.objects.get(employee=employee, date=date.today())
        except WorkTimeTracking.DoesNotExist:
            return Response({'error': 'Запись не найдена'}, status=404)

        serializer = WorkTimeTrackingSerializer(tracking, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Запись обновлена'})
        return Response(serializer.errors, status=400)

# Удаление записи о рабочем дне сотрудника по дате
class DeleteWorkTimeTrackingAPIView(APIView):
    permission_classes = [IsSessionAuthenticated, roleRequiredPermissionFactory(['admin'])]
    
    def delete(self, request):
        personnel_number = request.data.get('personnelNumber')
        date_str = request.data.get('date')  # в формате 'YYYY-MM-DD'

        if not personnel_number or not date_str:
            return Response({'error': 'personnelNumber и date обязательны'}, status=400)

        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return Response({'error': 'Некорректный формат даты. Используйте YYYY-MM-DD'}, status=400)

        try:
            employee = Employee.objects.get(personnelNumber=personnel_number)
        except Employee.DoesNotExist:
            return Response({'error': 'Сотрудник не найден'}, status=404)

        tracking = WorkTimeTracking.objects.filter(employee=employee, date=date_obj).last()
        if not tracking:
            return Response({'error': 'Запись не найдена'}, status=404)

        tracking.delete()
        return Response({'message': 'Запись удалена'}, status=204)

class ListWorkTimeTrackingAPIView(APIView):
    permission_classes = [
        IsSessionAuthenticated, 
        roleRequiredPermissionFactory([
            'admin', 'hr', 'marketer',
            'foreman', 'storekeeper', 'basic'
        ])
    ]

    def get(self, request):
        full_name = request.query_params.get('fullName')
        personnel_number = request.query_params.get('personnelNumber')

        queryset = WorkTimeTracking.objects.all()

        if personnel_number:
            queryset = queryset.filter(employee__personnelNumber=personnel_number)

        if full_name:
            queryset = queryset.filter(employee__fullName__icontains=full_name)

        serializer = WorkTimeTrackingSerializer(queryset, many=True)
        return Response(serializer.data)

### Роли ###

class RoleViewSet(viewsets.ModelViewSet):
    permission_classes = [IsSessionAuthenticated, roleRequiredPermissionFactory(['admin'])]

    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    # permission_classes = [IsAuthenticatedOrReadOnly]  # при необходимости

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        role_name = instance.name  # можно использовать для текста
        self.perform_destroy(instance)
        return Response(
            {"message": f"Роль '{role_name}' успешно удалена"},
            status=status.HTTP_200_OK
        )