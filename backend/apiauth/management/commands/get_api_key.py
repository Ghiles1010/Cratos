"""Management command to get API key for an existing user."""
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from apiauth.models import APIKey

User = get_user_model()


class Command(BaseCommand):
    help = 'Get API key for a user (creates if none exists). Requires username and password.'

    def add_arguments(self, parser):
        parser.add_argument('--username', required=True, help='Username')
        parser.add_argument('--password', required=True, help='Password')

    def handle(self, *args, **options):
        username = options['username']
        password = options['password']

        # Authenticate user
        user = User.objects.filter(username=username).first()
        if user is None:
            raise CommandError(f'User "{username}" does not exist.')

        if not user.check_password(password):
            raise CommandError('Invalid password.')

        if not user.is_active:
            raise CommandError('User account is disabled.')

        # Get or create API key
        api_key, created = APIKey.objects.get_or_create(
            user=user,
            defaults={'key': APIKey.generate_key()},
        )

        if created:
            self.stdout.write(self.style.SUCCESS(f'Created API key for user: {user.username}'))
        else:
            self.stdout.write(f'API key already exists for user: {user.username}')

        self.stdout.write(self.style.SUCCESS(f'API Key: {api_key.key}'))



