import datetime
from collections import defaultdict

from django.test import TestCase

from turtlemail import stats
from turtlemail.models import User, Location, Stay
from turtlemail.tests import TestLocations


class TestDataMixin:
    def setUp(self):
        user1, user2, user3, user4 = [
            User.objects.create(email=f"{username}@turtlemail.app", username=username)
            for username in ["user1", "user2", "user3", "user4"]
        ]

        locations = defaultdict(list)
        for user in [user1, user2, user3, user4]:
            for test_location in TestLocations:
                locations[user].append(
                    Location.objects.create(
                        is_home=False, point=test_location.value, user=user
                    )
                )

        Stay.objects.create(
            location=locations[user1][0],
            user=user1,
            frequency=Stay.ONCE,
            start=datetime.date(2024, 2, 1),
            end=datetime.date(2024, 2, 10),
        )
        Stay.objects.create(
            location=locations[user1][1],
            user=user1,
            frequency=Stay.WEEKLY,
        )
        Stay.objects.create(
            location=locations[user1][2],
            user=user1,
            frequency=Stay.SOMETIMES,
        )
        Stay.objects.create(
            location=locations[user2][3],
            user=user2,
            frequency=Stay.WEEKLY,
        )
        Stay.objects.create(
            location=locations[user3][0],
            user=user3,
            frequency=Stay.SOMETIMES,
        )
        Stay.objects.create(
            location=locations[user4][1],
            user=user4,
            frequency=Stay.WEEKLY,
        )
        Stay.objects.create(
            location=locations[user4][2],
            user=user4,
            frequency=Stay.SOMETIMES,
        )
        Stay.objects.create(
            location=locations[user4][0],
            user=user4,
            frequency=Stay.SOMETIMES,
            deleted=True,
        )


class StatsTestCase(TestDataMixin, TestCase):
    def test_account_numbers(self):
        self.assertEqual(
            stats.get_account_stats(),
            {"total_number": 4},
        )

    def test_number_of_stays(self):
        self.assertEqual(stats.get_stay_stats(), {"min": 1, "max": 3, "median": 1.5})
