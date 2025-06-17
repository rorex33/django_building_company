from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password

from api.models import Role, CustomUser

class Command(BaseCommand):
    help = 'Создание предустановленных ролей и администратора'

    def handle(self, *args, **kwargs):
        roles = [
            {'name': 'admin', 'description': 'Администратор'},
            {'name': 'hr', 'description': 'Отдел кадров'},
            {'name': 'marketer', 'description': 'Маркетолог'},
            {'name': 'foreman', 'description': 'Прораб'},
            {'name': 'storekeeper', 'description': 'Кладовщик'},
            {'name': 'basic', 'description': 'Базовый пользователь'},
        ]

        for role in roles:
            obj, created = Role.objects.get_or_create(
                name=role['name'],
                defaults={'description': role['description']}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Создана роль: {role["name"]}'))
            else:
                self.stdout.write(f'Роль уже существует: {role["name"]}')

        if not CustomUser.objects.filter(login='admin').exists():
            admin_role = Role.objects.get(name='admin')
            admin = CustomUser.objects.create(
                login='admin',
                role=admin_role,
                _password=make_password('admin123')
            )
            self.stdout.write(self.style.SUCCESS('Создан админ: login=admin, password=admin123'))
        else:
            self.stdout.write('Админ уже существует.')
