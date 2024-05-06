from datetime import date, datetime, timedelta
from typing import List
from django.contrib.gis.geos import Point
from django.test import TestCase

from turtlemail import routing
from turtlemail.models import Location, Packet, Stay, User


HAMBURG = Point(9.58292, 53.33145)
BERLIN = Point(13.431700, 52.592879)
MUNICH = Point(11.33371, 48.08565)
BREMEN = Point(53.04052, 8.56428)

POINTS = {
    "Hamburg": HAMBURG,
    "Berlin": BERLIN,
    "Munich": MUNICH,
    "Bremen": BREMEN,
}


class ReachableStaysTestCase(TestCase):
    def setUp(self):
        self.sender = User.objects.create(
            email="sender@turtlemail.app", username="sender"
        )
        location = Location.objects.create(
            is_home=False, point=HAMBURG, user=self.sender
        )
        self.start_stay = Stay.objects.create(
            location=location,
            user=self.sender,
            frequency=Stay.ONCE,
            start=datetime(2024, 2, 1),
            end=datetime(2024, 2, 10),
        )

        self.other_user = User.objects.create(
            email="other@turtlemail.app", username="other"
        )
        location = Location.objects.create(
            is_home=False, point=HAMBURG, user=self.other_user
        )
        self.reachable_stay_time_unknown = Stay.objects.create(
            location=location, user=self.other_user, frequency=Stay.DAILY
        )
        self.reachable_stay_time_overlaps = Stay.objects.create(
            location=location,
            user=self.other_user,
            frequency=Stay.ONCE,
            start=datetime(2024, 1, 1),
            end=datetime(2024, 2, 20),
        )
        self.reachable_stay_same_user = Stay.objects.create(
            location=location,
            user=self.sender,
            frequency=Stay.ONCE,
            start=datetime(2024, 3, 1),
            end=datetime(2024, 3, 2),
        )
        self.unreachable_stay_wrong_time = Stay.objects.create(
            location=location,
            user=self.other_user,
            frequency=Stay.ONCE,
            start=datetime(2024, 1, 1),
            end=datetime(2024, 1, 10),
        )
        unreachable_location = Location.objects.create(
            is_home=False, point=BERLIN, user=self.other_user
        )
        self.unreachable_stay_wrong_location = Stay.objects.create(
            location=unreachable_location, user=self.other_user, frequency=Stay.ONCE
        )

    def test_reachable_stays(self):
        reachable = routing.get_reachable_stays(self.start_stay, set())
        self.assertEqual(
            set(reachable),
            {
                self.reachable_stay_time_unknown,
                self.reachable_stay_time_overlaps,
                self.reachable_stay_same_user,
            },
        )

    def test_exclude_visited_stays(self):
        reachable = routing.get_reachable_stays(
            self.start_stay,
            {self.reachable_stay_time_overlaps.id},
        )
        self.assertFalse(self.reachable_stay_time_overlaps in set(reachable))


class EstimatedHandoverTestCase(TestCase):
    def setUp(self):
        self.sender = User.objects.create(
            email="sender@turtlemail.app", username="sender"
        )
        location = Location.objects.create(
            is_home=False, point=HAMBURG, user=self.sender
        )

        self.previous_handover = (date(2024, 1, 3), date(2024, 1, 5))

        self.cases = [
            (
                Stay.objects.create(
                    location=location,
                    user=self.sender,
                    frequency=Stay.ONCE,
                    start=date(2024, 1, 1),
                    end=date(2024, 1, 10),
                ),
                (date(2024, 1, 3), date(2024, 1, 5)),
            ),
            (
                Stay.objects.create(
                    location=location,
                    user=self.sender,
                    frequency=Stay.ONCE,
                    start=date(2024, 1, 5),
                    end=date(2024, 1, 10),
                ),
                (date(2024, 1, 5), date(2024, 1, 5)),
            ),
            (
                Stay.objects.create(
                    location=location,
                    user=self.sender,
                    frequency=Stay.DAILY,
                ),
                (date(2024, 1, 4), date(2024, 1, 7)),
            ),
            (
                Stay.objects.create(
                    location=location,
                    user=self.sender,
                    frequency=Stay.WEEKLY,
                ),
                (date(2024, 1, 4), date(2024, 1, 12)),
            ),
            (
                Stay.objects.create(
                    location=location,
                    user=self.sender,
                    frequency=Stay.SOMETIMES,
                ),
                (
                    date(2024, 1, 3) + timedelta(days=14),
                    date(2024, 1, 5) + timedelta(days=30),
                ),
            ),
        ]

    def test_estimate_handover_dates(self):
        for stay, expected_handover in self.cases:
            date = routing.get_estimated_handover_range(self.previous_handover, stay)
            self.assertEqual(date, expected_handover)


class FindRouteTestCase(TestCase):
    def stay_for(self, user: User, name: str, frequency=Stay.WEEKLY):
        location = Location.objects.create(
            is_home=False, point=POINTS[name], user=user, name=name
        )
        return Stay.objects.create(location=location, user=user, frequency=frequency)

    def stays_from_nodes(self, nodes: List[routing.RoutingNode]):
        return [node.stay for node in nodes]

    def setUp(self) -> None:
        self.sender = User.objects.create(
            email="sender@turtlemail.app", username="sender"
        )
        self.recipient = User.objects.create(
            email="recipient@turtlemail.app", username="recipient"
        )
        self.packet = Packet.objects.create(
            sender=self.sender, recipient=self.recipient, human_id="test_id"
        )

    def test_find_route(self):
        self.expected_stays = []
        self.expected_stays.append(self.stay_for(user=self.sender, name="Hamburg"))
        self.expected_stays.append(self.stay_for(user=self.sender, name="Berlin"))

        intermediate_user = User.objects.create(
            email="intermediate@turtlemail.app", username="intermediate"
        )
        self.expected_stays.append(self.stay_for(user=intermediate_user, name="Berlin"))
        self.expected_stays.append(self.stay_for(user=intermediate_user, name="Munich"))
        self.stay_for(user=intermediate_user, name="Bremen")

        self.expected_stays.append(self.stay_for(user=self.recipient, name="Munich"))

        nodes = routing.find_route(self.packet)
        self.assertIsNotNone(nodes)
        self.assertEqual(self.expected_stays, self.stays_from_nodes(nodes))

    def test_find_no_route_max_duration(self):
        calculation_date = date(2024, 1, 1)
        self.stay_for(user=self.sender, name="Hamburg")
        self.stay_for(user=self.sender, name="Munich")

        self.stay_for(
            user=self.recipient,
            name="Munich",
            frequency=Stay.ONCE,
            start=date(2024, 4, 10),
            end=date(2024, 4, 20),
        )

        nodes: List[routing.RoutingNode] = routing.find_route(
            self.packet, calculation_date=calculation_date
        )  # type: ignore
        self.assertIsNone(nodes)

    def test_find_route_prioritize_faster_stays(self):
        self.expected_stays = []
        self.expected_stays.append(self.stay_for(user=self.sender, name="Hamburg"))
        # There's a Direct route from Hamburg to Munich, but it's only a SOMETIMES
        # frequency. We'd expect the system to choose the indirect connection
        # with the DAILY frequency because it's faster.

        # This is the direct, but long route:
        slow_user = User.objects.create(email="slow@turtlemail.app", username="slow")
        self.stay_for(user=slow_user, name="Hamburg", frequency=Stay.WEEKLY)
        self.stay_for(user=slow_user, name="Munich", frequency=Stay.SOMETIMES)

        # This is the indirect route that's faster:
        self.expected_stays.append(
            self.stay_for(user=self.sender, name="Berlin", frequency=Stay.WEEKLY)
        )
        fast_user = User.objects.create(email="fast@turtlemail.app", username="fast")
        self.expected_stays.append(
            self.stay_for(user=fast_user, name="Berlin", frequency=Stay.WEEKLY)
        )
        self.expected_stays.append(
            self.stay_for(
                user=fast_user,
                name="Munich",
                frequency=Stay.DAILY,
            )
        )

        self.expected_stays.append(self.stay_for(user=self.recipient, name="Munich"))

        nodes = routing.find_route(self.packet)
        self.assertIsNotNone(nodes)
        self.assertEqual(self.expected_stays, self.stays_from_nodes(nodes))

    def test_impossible_route_no_stays(self):
        route = routing.find_route(self.packet)
        self.assertEqual(None, route)

    def test_impossible_route_disconnected_stays(self):
        self.stay_for(user=self.sender, name="Hamburg")
        self.stay_for(user=self.sender, name="Berlin")

        self.stay_for(user=self.recipient, name="Bremen")

        self.stay_for(user=self.recipient, name="Munich")

        route = routing.find_route(self.packet)
        self.assertEqual(None, route)
