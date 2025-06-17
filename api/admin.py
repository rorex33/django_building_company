from django.contrib import admin

# Импорт моделей
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

admin.site.register([
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
])