from datetime import date
from django.contrib.gis.geos import Point
from django.test import TestCase

from turtlemail.models import Location, Packet, Route, RouteStep, Stay, User


class ReachableStaysTestCase(TestCase):
    def setUp(self):
        sender = User.objects.create(email="sender@turtlemail.app", username="sender")
        recipient = User.objects.create(
            email="recipient@turtlemail.app", username="recipient"
        )
        location = Location.objects.create(
            is_home=False, point=Point(0, 0), user=sender
        )
        self.stay = Stay.objects.create(location=location, user=sender)

        self.packet = Packet.objects.create(
            sender=sender, recipient=recipient, human_id="test_id"
        )
        self.route = Route.objects.create(packet=self.packet)

    def test_overlapping_date_range_not_overlapping(self):
        step_1 = RouteStep.objects.create(
            stay=self.stay,
            start=date(2024, 5, 30),
            end=date(2024, 5, 31),
            packet=self.packet,
            route=self.route,
        )
        step_2 = RouteStep.objects.create(
            stay=self.stay,
            start=date(2024, 6, 10),
            end=date(2024, 6, 14),
            previous_step=step_1,
            packet=self.packet,
            route=self.route,
        )

        overlapping_range = step_1.get_overlapping_date_range(step_2)
        self.assertEqual((None, None), overlapping_range)

    def test_overlapping_date_range_not_overlapping_2(self):
        step_1 = RouteStep.objects.create(
            stay=self.stay,
            start=date(2024, 6, 20),
            end=date(2024, 6, 21),
            packet=self.packet,
            route=self.route,
        )
        step_2 = RouteStep.objects.create(
            stay=self.stay,
            start=date(2024, 5, 10),
            end=date(2024, 5, 14),
            previous_step=step_1,
            packet=self.packet,
            route=self.route,
        )

        overlapping_range = step_1.get_overlapping_date_range(step_2)
        self.assertEqual((None, None), overlapping_range)

    def test_overlapping_date_range_overlapping(self):
        step_1 = RouteStep.objects.create(
            stay=self.stay,
            start=date(2024, 5, 30),
            end=date(2024, 6, 5),
            packet=self.packet,
            route=self.route,
        )
        step_2 = RouteStep.objects.create(
            stay=self.stay,
            start=date(2024, 6, 3),
            end=date(2024, 6, 14),
            previous_step=step_1,
            packet=self.packet,
            route=self.route,
        )

        overlapping_range = step_1.get_overlapping_date_range(step_2)
        self.assertEqual((date(2024, 6, 3), date(2024, 6, 5)), overlapping_range)

        overlapping_range = step_2.get_overlapping_date_range(step_1)
        self.assertEqual((date(2024, 6, 3), date(2024, 6, 5)), overlapping_range)
