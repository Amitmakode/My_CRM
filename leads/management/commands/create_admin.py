from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Create superuser'

    def handle(self, *args, **kwargs):
        try:
            if not User.objects.filter(username='admin').exists():
                User.objects.create_superuser('admin', 'admin@admin.com', 'Admin@123')
                self.stdout.write(self.style.SUCCESS('Superuser created successfully'))
            else:
                self.stdout.write(self.style.SUCCESS('Superuser already exists'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {e}'))
