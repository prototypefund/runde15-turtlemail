from django.core.management import BaseCommand, call_command
from turtlemail.models import User


class Command(BaseCommand):
    def handle(self, *args, **options):
        """fill database with initial data and set userpasswords"""

        call_command("loaddata", "initial_data.yaml")
        for user in User.objects.all():
            user.set_password("testpassword")
            user.save()
