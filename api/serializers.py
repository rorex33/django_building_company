from rest_framework import serializers
from .models import (
    Role, Right, RoleRight, User, Object, JobTitle, Employee,
    ClientsApplication, ClientsApplicationType, ClientsApplicationStatus,
    WorkTimeTracking, Material
)

class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = '__all__'


class RightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Right
        fields = '__all__'


class RoleRightSerializer(serializers.ModelSerializer):
    role = RoleSerializer(read_only=True)
    right = RightSerializer(read_only=True)
    role_id = serializers.PrimaryKeyRelatedField(queryset=Role.objects.all(), source='role', write_only=True)
    right_id = serializers.PrimaryKeyRelatedField(queryset=Right.objects.all(), source='right', write_only=True)

    class Meta:
        model = RoleRight
        fields = ['id', 'role', 'right', 'role_id', 'right_id']


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'login', 'password', 'role']

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.password = password
        user.save()
        return user

    def update(self, instance, validated_data):
        if 'password' in validated_data:
            instance.password = validated_data.pop('password')
        return super().update(instance, validated_data)


class ObjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Object
        fields = '__all__'


class JobTitleSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobTitle
        fields = '__all__'


class EmployeeSerializer(serializers.ModelSerializer):
    jobTitle = JobTitleSerializer(read_only=True)
    object = ObjectSerializer(read_only=True)
    user = UserSerializer(read_only=True)

    jobTitle_id = serializers.PrimaryKeyRelatedField(queryset=JobTitle.objects.all(), source='jobTitle', write_only=True)
    object_id = serializers.PrimaryKeyRelatedField(queryset=Object.objects.all(), source='object', write_only=True)
    user_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), source='user', write_only=True, allow_null=True, required=False)

    class Meta:
        model = Employee
        fields = [
            'id', 'fullName', 'personnelNumber', 'phoneNumber', 'email',
            'bankDetails', 'passport', 'jobTitle', 'object', 'user',
            'jobTitle_id', 'object_id', 'user_id'
        ]


class ClientsApplicationTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientsApplicationType
        fields = '__all__'


class ClientsApplicationStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientsApplicationStatus
        fields = '__all__'


class ClientsApplicationSerializer(serializers.ModelSerializer):
    type = ClientsApplicationTypeSerializer(read_only=True)
    status = ClientsApplicationStatusSerializer(read_only=True)
    type_id = serializers.PrimaryKeyRelatedField(queryset=ClientsApplicationType.objects.all(), source='type', write_only=True)
    status_id = serializers.PrimaryKeyRelatedField(queryset=ClientsApplicationStatus.objects.all(), source='status', write_only=True)

    class Meta:
        model = ClientsApplication
        fields = ['id', 'fullName', 'phoneNumber', 'description', 'date', 'type', 'status', 'type_id', 'status_id']


class WorkTimeTrackingSerializer(serializers.ModelSerializer):
    employee = EmployeeSerializer(read_only=True)
    employee_id = serializers.PrimaryKeyRelatedField(queryset=Employee.objects.all(), source='employee', write_only=True)

    class Meta:
        model = WorkTimeTracking
        fields = ['id', 'employee', 'employee_id', 'date', 'startTime', 'endTime']


class MaterialSerializer(serializers.ModelSerializer):
    object = ObjectSerializer(read_only=True)
    object_id = serializers.PrimaryKeyRelatedField(queryset=Object.objects.all(), source='object', write_only=True)

    class Meta:
        model = Material
        fields = ['id', 'name', 'amount', 'object', 'object_id']
