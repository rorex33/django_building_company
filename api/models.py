from django.db import models
from django.contrib.auth.hashers import make_password, check_password

class Role(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class CustomUser(models.Model):
    login = models.CharField(max_length=100, unique=True)
    _password = models.CharField(max_length=128, db_column='password')
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True)

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, raw_password):
        self._password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self._password)

    def save(self, *args, **kwargs):
    # Если пароль был изменён и не хеширован
        if self._password and not self._password.startswith('pbkdf2_'):
            self.password = self._password  # Вызовет @password.setter
        super().save(*args, **kwargs)

    def __str__(self):
        return self.login

class Object(models.Model):
    name = models.CharField(max_length=100)
    address = models.TextField()
    description = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return self.name

class JobTitle(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Employee(models.Model):
    fullName = models.CharField(max_length=200)
    personnelNumber = models.CharField(max_length=50, unique=True)
    phoneNumber = models.CharField(max_length=20)
    email = models.EmailField()
    bankDetails = models.TextField()
    passport = models.TextField()
    jobTitle = models.ForeignKey(JobTitle, on_delete=models.SET_NULL, null=True)
    object = models.ForeignKey(Object, on_delete=models.SET_NULL, null=True)
    user = models.OneToOneField(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.fullName

class ClientsApplicationStatus(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class ClientsApplicationType(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class ClientsApplication(models.Model):
    fullName = models.CharField(max_length=200)
    phoneNumber = models.CharField(max_length=20)
    description = models.TextField()
    type = models.ForeignKey(ClientsApplicationType, on_delete=models.SET_NULL, null=True)
    status = models.ForeignKey(ClientsApplicationStatus, on_delete=models.SET_NULL, null=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.fullName} - {self.type.name}"

class WorkTimeTracking(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    date = models.DateField()
    startTime = models.TimeField()
    endTime = models.TimeField(null=True)

    def __str__(self):
        return f"{self.employee.fullName} - {self.date}"

class Material(models.Model):
    name = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    object = models.ForeignKey(Object, on_delete=models.CASCADE)

    def __str__(self):
        return self.name