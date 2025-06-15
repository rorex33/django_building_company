from django.contrib import admin

# Импорт моделей
from .models import (
    Role, Right, RoleRight, User, Object, JobTitle, Employee,
    ClientsApplication, ClientsApplicationType, ClientsApplicationStatus,
    WorkTimeTracking, Material
)

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('login', 'role')
    exclude = ('_password',)  # Скрыть поле хеша пароля

admin.site.register([
    Material, WorkTimeTracking, ClientsApplication,
    ClientsApplicationType, ClientsApplicationStatus,
    Employee, JobTitle, Object, RoleRight, Right, Role
])