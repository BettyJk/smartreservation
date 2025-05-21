# dashboard/management/commands/create_user.py
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

class Command(BaseCommand):
    help = 'Creates a custom user account'

    def add_arguments(self, parser):
        parser.add_argument('--email', required=True)
        parser.add_argument('--role', required=True)
        parser.add_argument('--filiere', default='')
        parser.add_argument('--year', default='')
        parser.add_argument('--password', default='ensam2024')

    def handle(self, *args, **options):
        User = get_user_model()
        
        try:
            user = User.objects.create_user(
                email=options['email'],
                first_name='Test',
                last_name='User',
                role=options['role'],
                password=options['password'],
                filiere=options['filiere'],
                year=options['year']
            )
            self.stdout.write(self.style.SUCCESS(f'Successfully created {options["role"]} user: {options["email"]}'))
        except ValidationError as e:
            self.stdout.write(self.style.ERROR(f'Error: {e}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Unexpected error: {str(e)}'))