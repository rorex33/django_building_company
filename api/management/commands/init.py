from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password

from api.models import Role, CustomUser, ClientsApplicationStatus, ClientsApplicationType

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

        # --- Администратор ---
        if not CustomUser.objects.filter(login='admin').exists():
            admin_role = Role.objects.get(name='admin')
            admin = CustomUser.objects.create(
                login='admin',
                role=admin_role,
                _password=make_password('admin123')  # Предположим, поле называется _password
            )
            self.stdout.write(self.style.SUCCESS('Создан админ: login=admin, password=admin123'))
        else:
            self.stdout.write('Админ уже существует.')

        # --- Статусы заявки ---
        status_obj, status_created = ClientsApplicationStatus.objects.get_or_create(
            name='Новая',
            defaults={'description': 'Новая заявка'}
        )
        if status_created:
            self.stdout.write(self.style.SUCCESS('Создан статус заявки: Новая'))
        else:
            self.stdout.write('Статус заявки "Новая" уже существует.')

        # --- Типы заявки ---
        type_obj, type_created = ClientsApplicationType.objects.get_or_create(
            name='Обратный звонок',
            defaults={'description': 'Клиент хочет, чтобы ему перезвонили'}
        )
        if type_created:
            self.stdout.write(self.style.SUCCESS('Создан тип заявки: Обратный звонок'))
        else:
            self.stdout.write('Тип заявки "Обратный звонок" уже существует.')