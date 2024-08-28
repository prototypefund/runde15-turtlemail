from django.core.management import BaseCommand, call_command
from turtlemail.models import User


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "--demo",
            action="store_true",
            help="Load demo data instead of development data",
        )

    def handle(self, *args, **options):
        """fill database with initial data and set userpasswords"""

        data_file = "dev_data.yaml"
        if options["demo"]:
            data_file = "demo_data.yaml"
        call_command("loaddata", data_file)
        for user in User.objects.all():
            user.set_password("testpassword")
            user.save()
