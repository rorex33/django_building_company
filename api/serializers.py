from rest_framework import serializers
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


### ПОЛЬЗОВАТЕЛИ ###

class CustomUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    role = serializers.CharField(write_only=False)

    class Meta:
        model = CustomUser

        fields = ['id', 'login', 'password', 'role']
        extra_kwargs = {
            'role': {'write_only': True}  # Скрываем в ответе
        }

    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("Пароль должен содержать минимум 8 символов")
        return value

    def validate_role(self, value):
        """Проверяем существование роли"""
        if not Role.objects.filter(name=value).exists():
            raise serializers.ValidationError("Роль с таким названием не существует")
        return value

    def create(self, validated_data):
        # Получаем объект роли по названию
        role_name = validated_data.pop('role')
        role = Role.objects.get(name=role_name)
        
        # Создаем пользователя
        password = validated_data.pop('password')
        user = CustomUser(**validated_data, role=role)
        user.password = password  # Автоматическое хеширование через setter
        user.save()

        return user

    def update(self, instance, validated_data):
        if 'password' in validated_data:
            instance.password = validated_data.pop('password')
        return super().update(instance, validated_data)


### СОТРУДНИКИ ###

class EmployeeSerializer(serializers.ModelSerializer):
    jobTitle = serializers.CharField(write_only=False, required=False)
    object = serializers.CharField(write_only=False, required=False)
    user = serializers.CharField(write_only=False, required=False, allow_null=True, allow_blank=True)

    class Meta:
        model = Employee
        fields = [
            'id', 'fullName', 'personnelNumber', 'phoneNumber', 'email',
            'bankDetails', 'passport', 'jobTitle', 'object', 'user'
        ]

    def validate_personnelNumber(self, value):
        # Проверка только при создании или если поле обновляется
        if self.instance and self.instance.personnelNumber == value:
            return value
        if Employee.objects.filter(personnelNumber=value).exists():
            raise serializers.ValidationError("Сотрудник с таким табельным номером уже существует.")
        return value

    def validate_user(self, value):
        if not value:
            return None
        try:
            user = CustomUser.objects.get(login=value)
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError("Пользователь с таким логином не найден.")
        if self.instance and self.instance.user == user:
            return user
        if Employee.objects.filter(user=user).exists():
            raise serializers.ValidationError("Пользователь уже привязан к другому сотруднику.")
        return user

    def validate_jobTitle(self, value):
        from .models import JobTitle
        try:
            return JobTitle.objects.get(name=value)
        except JobTitle.DoesNotExist:
            raise serializers.ValidationError("Должность с таким названием не найдена.")

    def validate_object(self, value):
        from .models import Object
        try:
            return Object.objects.get(name=value)
        except Object.DoesNotExist:
            raise serializers.ValidationError("Объект с таким названием не найден.")

    def create(self, validated_data):
        user = validated_data.pop('user', None)
        job_title = validated_data.pop('jobTitle')
        obj = validated_data.pop('object')
        return Employee.objects.create(
            user=user,
            jobTitle=job_title,
            object=obj,
            **validated_data
        )


### ДОЛЖНОСТИ ###

class JobTitleSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobTitle
        fields = ['id', 'name']

    def validate_name(self, value):
        if JobTitle.objects.filter(name=value).exists():
            raise serializers.ValidationError("Должность с таким названием уже существует.")
        return value


### ОБЪЕКТЫ ###

class ObjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Object
        fields = ['id', 'name', 'address', 'description']

    def validate_name(self, value):
        # При редактировании: исключаем текущий объект из фильтра
        object_id = self.instance.id if self.instance else None
        if Object.objects.filter(name=value).exclude(id=object_id).exists():
            raise serializers.ValidationError("Объект с таким названием уже существует.")
        return value


### МАТЕРИАЛЫ ###

class MaterialSerializer(serializers.ModelSerializer):
    object = serializers.SlugRelatedField(
        slug_field='name',
        queryset=Object.objects.all()
    )
    object_data = ObjectSerializer(source='object', read_only=True)

    class Meta:
        model = Material
        fields = ['id', 'name', 'amount', 'object', 'object_data']

### ЗАЯВКИ ###

class ClientsApplicationTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientsApplicationType
        fields = ['id', 'name', 'description']

class ClientsApplicationStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientsApplicationStatus
        fields = ['id', 'name', 'description']

class ClientsApplicationSerializer(serializers.ModelSerializer):
    type = ClientsApplicationTypeSerializer(read_only=True)
    status = ClientsApplicationStatusSerializer(read_only=True)
    
    type_name = serializers.SlugRelatedField(
        queryset=ClientsApplicationType.objects.all(),
        slug_field='name',
        source='type',
        write_only=True,
        required=False
    )
    status_name = serializers.SlugRelatedField(
        queryset=ClientsApplicationStatus.objects.all(),
        slug_field='name',
        source='status',
        write_only=True,
        required=False
    )

    class Meta:
        model = ClientsApplication
        fields = [
            'id', 'fullName', 'phoneNumber', 'description', 
            'date', 'type', 'status', 'type_name', 'status_name'
        ]


### WTT ###

class WorkTimeTrackingSerializer(serializers.ModelSerializer):
    employee = EmployeeSerializer(read_only=True)
    personnelNumber = serializers.CharField(write_only=True)

    class Meta:
        model = WorkTimeTracking
        fields = ['id', 'employee', 'personnelNumber', 'date', 'startTime', 'endTime']

    def validate(self, data):
        start = data.get('startTime') or self.instance.startTime if self.instance else None
        end = data.get('endTime') or self.instance.endTime if self.instance else None

        if start and end and start > end:
            raise serializers.ValidationError("startTime не может быть позже endTime")
        return data

    def create(self, validated_data):
        personnel_number = validated_data.pop('personnelNumber')
        employee = Employee.objects.get(personnelNumber=personnel_number)
        return WorkTimeTracking.objects.create(employee=employee, **validated_data)

    def update(self, instance, validated_data):
        if 'date' in validated_data:
            raise serializers.ValidationError({"date": "Изменение даты не разрешено"})
        validated_data.pop('personnelNumber', None)
        return super().update(instance, validated_data)

class StartWorkSerializer(serializers.Serializer):
    personnelNumber = serializers.CharField()

    def validate_personnelNumber(self, value):
        try:
            return Employee.objects.get(personnelNumber=value)
        except Employee.DoesNotExist:
            raise serializers.ValidationError("Сотрудник с таким табельным номером не найден")

class EndWorkSerializer(serializers.Serializer):
    personnelNumber = serializers.CharField()

    def validate_personnelNumber(self, value):
        try:
            return Employee.objects.get(personnelNumber=value)
        except Employee.DoesNotExist:
            raise serializers.ValidationError("Сотрудник с таким табельным номером не найден")


### Роли ###

class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['id', 'name', 'description']

    def validate_name(self, value):
        # Проверяем уникальность для create и update
        qs = Role.objects.filter(name=value)
        if self.instance:
            qs = qs.exclude(id=self.instance.id)
        if qs.exists():
            raise serializers.ValidationError("Роль с таким названием уже существует.")
        return value
