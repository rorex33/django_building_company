from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.authentication import TokenAuthentication
from django.shortcuts import get_object_or_404
from functools import wraps
from django.utils import timezone
from datetime import timedelta, datetime

from .models import Right, RoleRight, Employee, WorkTimeTracking, Object, Material, ClientsApplication, ClientsApplicationType, ClientsApplicationStatus, User
from .serializers import EmployeeSerializer, WorkTimeTrackingSerializer, ObjectSerializer, MaterialSerializer, ClientsApplicationSerializer, ClientsApplicationTypeSerializer, ClientsApplicationStatusSerializer, UserSerializer

# Декоратор для проверки прав

def require_right(right_action):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(self, request, *args, **kwargs):
            user = request.user
            if not user.is_authenticated:
                return Response({"detail": "Authentication credentials were not provided."}, status=status.HTTP_401_UNAUTHORIZED)

            role = user.role
            if not role:
                return Response({"detail": "User has no assigned role."}, status=status.HTTP_403_FORBIDDEN)

            if not RoleRight.objects.filter(role=role, right__action=right_action).exists():
                return Response({"detail": f"Access denied: missing '{right_action}' permission."}, status=status.HTTP_403_FORBIDDEN)

            return view_func(self, request, *args, **kwargs)

        return _wrapped_view
    return decorator

# === Общее для всех пользователей ===
class MyWTTView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try:
            employee = request.user.employee
        except Employee.DoesNotExist:
            return Response({"detail": "User is not linked to any employee."}, status=status.HTTP_400_BAD_REQUEST)

        month_ago = timezone.now().date() - timedelta(days=30)
        records = WorkTimeTracking.objects.filter(employee=employee, date__gte=month_ago)
        serializer = WorkTimeTrackingSerializer(records, many=True)
        return Response(serializer.data)

class StartWorkView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    @require_right('track_time')
    def post(self, request):
        try:
            employee = request.user.employee
        except Employee.DoesNotExist:
            return Response({"detail": "User is not linked to any employee."}, status=status.HTTP_400_BAD_REQUEST)

        now = timezone.now()
        WorkTimeTracking.objects.create(employee=employee, date=now.date(), startTime=now.time(), endTime=None)
        return Response({"detail": "Start time recorded."})

class EndWorkView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    @require_right('track_time')
    def post(self, request):
        try:
            employee = request.user.employee
        except Employee.DoesNotExist:
            return Response({"detail": "User is not linked to any employee."}, status=status.HTTP_400_BAD_REQUEST)

        today = timezone.now().date()
        record = WorkTimeTracking.objects.filter(employee=employee, date=today).last()
        if not record or record.endTime:
            return Response({"detail": "No start record found or already ended."}, status=status.HTTP_400_BAD_REQUEST)

        record.endTime = timezone.now().time()
        record.save()
        return Response({"detail": "End time recorded."})

# === HR ===
class EmployeeListView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    @require_right('view_employees')
    def get(self, request):
        employees = Employee.objects.all()
        serializer = EmployeeSerializer(employees, many=True)
        return Response(serializer.data)

class AddEmployeeView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    @require_right('add_employee')
    def post(self, request):
        serializer = EmployeeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UpdateEmployeeView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    @require_right('edit_employee')
    def put(self, request, pk):
        employee = get_object_or_404(Employee, pk=pk)
        serializer = EmployeeSerializer(employee, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DeleteEmployeeView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    @require_right('delete_employee')
    def delete(self, request, pk):
        employee = get_object_or_404(Employee, pk=pk)
        employee.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# === Foreman ===
class ObjectListView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    @require_right('view_objects')
    def get(self, request):
        objs = Object.objects.all()
        serializer = ObjectSerializer(objs, many=True)
        return Response(serializer.data)

class AddObjectView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    @require_right('add_object')
    def post(self, request):
        serializer = ObjectSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DeleteObjectView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    @require_right('delete_object')
    def delete(self, request, pk):
        obj = get_object_or_404(Object, pk=pk)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# === Storekeeper ===
class MaterialListView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    @require_right('view_materials')
    def get(self, request):
        materials = Material.objects.all()
        serializer = MaterialSerializer(materials, many=True)
        return Response(serializer.data)

class AddMaterialView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    @require_right('add_material')
    def post(self, request):
        serializer = MaterialSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DeleteMaterialView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    @require_right('delete_material')
    def delete(self, request, pk):
        material = get_object_or_404(Material, pk=pk)
        material.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# === Marketer ===
class ApplicationListView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    @require_right('view_applications')
    def get(self, request):
        applications = ClientsApplication.objects.all()
        serializer = ClientsApplicationSerializer(applications, many=True)
        return Response(serializer.data)

class UpdateApplicationView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    @require_right('edit_applications')
    def put(self, request, pk):
        application = get_object_or_404(ClientsApplication, pk=pk)
        serializer = ClientsApplicationSerializer(application, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# === Admin ===
class ManageAppTypesView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    @require_right('manage_app_types')
    def post(self, request):
        serializer = ClientsApplicationTypeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ManageAppStatusesView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    @require_right('manage_app_statuses')
    def post(self, request):
        serializer = ClientsApplicationStatusSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ManageUsersView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    @require_right('manage_users')
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
