import json

from django.core.management import BaseCommand
from turtlemail import stats


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "--demo",
            action="store_true",
            help="Load demo data instead of development data",
        )

    def handle(self, *args, **options):
        data = {
            "accounts": stats.get_account_stats(),
            "packets": stats.get_packet_stats(),
            "stays": stats.get_stay_stats(),
        }
        self.stdout.write(
            json.dumps(data, indent=4, sort_keys=True, ensure_ascii=False),
        )
