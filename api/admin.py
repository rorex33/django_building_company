from django.contrib import admin

# Импорт моделей
from .models import (
    Role, Right, RoleRight, CustomUser, Object, JobTitle, Employee,
    ClientsApplication, ClientsApplicationType, ClientsApplicationStatus,
    WorkTimeTracking, Material
)

admin.site.register([
    Material, WorkTimeTracking, CustomUser, ClientsApplication,
    ClientsApplicationType, ClientsApplicationStatus,
    Employee, JobTitle, Object, RoleRight, Right, Role
])