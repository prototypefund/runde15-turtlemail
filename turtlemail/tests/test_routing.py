from datetime import date, datetime, timedelta
from typing import List
from django.conf import settings
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
        self.recipient = User.objects.create(
            email="recipient@turtlemail.app", username="recipient"
        )
        self.packet = Packet.objects.create(
            sender=self.sender, recipient=self.recipient, human_id="test_id"
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
            is_home=False, point=HAMBURG, user=self.other_user, name="Hamburg"
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
            location=unreachable_location, user=self.other_user, frequency=Stay.DAILY
        )
        self.unreachable_stay_daily_inactive = Stay.objects.create(
            location=location,
            user=self.other_user,
            frequency=Stay.DAILY,
            inactive_until=datetime(2024, 2, 11),
        )
        self.unreachable_stay_once_inactive = Stay.objects.create(
            location=location,
            user=self.other_user,
            frequency=Stay.ONCE,
            start=datetime(2024, 1, 1),
            end=datetime(2024, 2, 20),
            inactive_until=datetime(2024, 2, 11),
        )

    def test_reachable_stays(self):
        reachable = routing.get_reachable_stays(
            self.start_stay, set(), date(2024, 1, 1)
        )
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
            self.start_stay, {self.reachable_stay_time_overlaps.id}, date(2024, 1, 1)
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

        self.previous_handover = date(2024, 1, 3)

        self.cases = [
            (
                Stay.objects.create(
                    location=location,
                    user=self.sender,
                    frequency=Stay.ONCE,
                    start=date(2024, 1, 1),
                    end=date(2024, 1, 10),
                ),
                date(2024, 1, 3),
            ),
            (
                Stay.objects.create(
                    location=location,
                    user=self.sender,
                    frequency=Stay.ONCE,
                    start=date(2024, 1, 5),
                    end=date(2024, 1, 10),
                ),
                date(2024, 1, 5),
            ),
            (
                Stay.objects.create(
                    location=location,
                    user=self.sender,
                    frequency=Stay.DAILY,
                ),
                date(2024, 1, 4),
            ),
            (
                Stay.objects.create(
                    location=location,
                    user=self.sender,
                    frequency=Stay.WEEKLY,
                ),
                date(2024, 1, 6),
            ),
            (
                Stay.objects.create(
                    location=location,
                    user=self.sender,
                    frequency=Stay.SOMETIMES,
                ),
                date(2024, 1, 3) + timedelta(days=14),
            ),
            (
                Stay.objects.create(
                    location=location,
                    user=self.sender,
                    frequency=Stay.DAILY,
                    inactive_until=date(2024, 1, 7),
                ),
                date(2024, 1, 4),
            ),
            (
                Stay.objects.create(
                    location=location,
                    user=self.sender,
                    frequency=Stay.ONCE,
                    start=date(2024, 1, 3),
                    end=date(2024, 1, 10),
                    inactive_until=date(2024, 1, 5),
                ),
                date(2024, 1, 3),
            ),
        ]

    def test_estimate_handover_dates(self):
        for stay, expected_handover in self.cases:
            date = routing.get_earliest_estimated_handover(self.previous_handover, stay)
            self.assertEqual(date, expected_handover)


class FindRouteTestCase(TestCase):
    def stay_for(
        self,
        user: User,
        name: str,
        frequency=Stay.WEEKLY,
        start=None,
        end=None,
        inactive_until=None,
    ):
        location = Location.objects.create(
            is_home=False, point=POINTS[name], user=user, name=name
        )
        return Stay.objects.create(
            location=location,
            user=user,
            frequency=frequency,
            start=start,
            end=end,
            inactive_until=inactive_until,
        )

    def stays_from_nodes(self, nodes: List[routing.RoutingNode]):
        return [node.stay for node in nodes]

    def assert_route_valid():
        # TODO check that all routesteps have overlapping times and correct date ranges
        pass

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
        expected_stays = []
        expected_handover_dates = []
        calculation_date = date(2024, 1, 1)
        expected_stays.append(self.stay_for(user=self.sender, name="Berlin"))
        expected_handover_dates.append((date(2024, 1, 1), date(2024, 1, 11)))

        intermediate_user = User.objects.create(
            email="intermediate@turtlemail.app", username="intermediate"
        )
        expected_stays.append(self.stay_for(user=intermediate_user, name="Berlin"))
        expected_handover_dates.append((date(2024, 1, 4), date(2024, 1, 18)))
        expected_stays.append(self.stay_for(user=intermediate_user, name="Munich"))
        expected_handover_dates.append((date(2024, 1, 11), date(2024, 1, 25)))
        self.stay_for(user=intermediate_user, name="Bremen")

        expected_stays.append(self.stay_for(user=self.recipient, name="Munich"))
        expected_handover_dates.append((date(2024, 1, 18), date(2024, 1, 29)))

        nodes: List[routing.RoutingNode] = routing.find_route(
            self.packet, calculation_date=calculation_date
        )  # type: ignore
        self.assertIsNotNone(nodes)
        stays = self.stays_from_nodes(nodes)
        self.assertEqual(expected_stays, stays)

        handover_dates = routing.calculate_routestep_dates(stays, calculation_date)
        self.assertEqual(expected_handover_dates, handover_dates)

    def test_find_route_trim_starting_stays(self):
        expected_stays = []
        calculation_date = date(2024, 1, 1)
        # This stay should be trimmed.
        # The algorithm will start looking here because it's most likely
        # that the user is currently at this location.
        # But the route should start in Berlin, since telling users
        # to transport their packet between their own stays
        # is confusing.
        self.stay_for(user=self.sender, name="Hamburg", frequency=Stay.DAILY)
        expected_stays.append(self.stay_for(user=self.sender, name="Berlin"))

        expected_stays.append(self.stay_for(user=self.recipient, name="Berlin"))

        nodes: List[routing.RoutingNode] = routing.find_route(
            self.packet, calculation_date=calculation_date
        )  # type: ignore
        self.assertIsNotNone(nodes)
        stays = self.stays_from_nodes(nodes)
        self.assertEqual(expected_stays, stays)

    def test_find_no_route_max_duration(self):
        calculation_date = date(2024, 1, 1)
        self.stay_for(user=self.sender, name="Hamburg")
        self.stay_for(user=self.sender, name="Munich")

        start = (
            calculation_date + settings.TURTLEMAIL_MAX_ROUTE_LENGTH + timedelta(days=1)
        )
        self.stay_for(
            user=self.recipient,
            name="Munich",
            frequency=Stay.ONCE,
            start=start,
            end=start + timedelta(days=10),
        )

        nodes: List[routing.RoutingNode] = routing.find_route(
            self.packet, calculation_date=calculation_date
        )  # type: ignore
        self.assertIsNone(nodes)

    def test_find_route_prioritize_faster_stays(self):
        expected_stays = []
        self.stay_for(user=self.sender, name="Hamburg")
        # There's a Direct route from Hamburg to Munich, but it's only a SOMETIMES
        # frequency. We'd expect the system to choose the indirect connection
        # with the DAILY frequency because it's faster.

        # This is the direct, but long route:
        slow_user = User.objects.create(email="slow@turtlemail.app", username="slow")
        self.stay_for(user=slow_user, name="Hamburg", frequency=Stay.WEEKLY)
        self.stay_for(user=slow_user, name="Munich", frequency=Stay.SOMETIMES)

        # This is the indirect route that's faster:
        expected_stays.append(
            self.stay_for(user=self.sender, name="Berlin", frequency=Stay.WEEKLY)
        )
        fast_user = User.objects.create(email="fast@turtlemail.app", username="fast")
        expected_stays.append(
            self.stay_for(user=fast_user, name="Berlin", frequency=Stay.WEEKLY)
        )
        expected_stays.append(
            self.stay_for(
                user=fast_user,
                name="Munich",
                frequency=Stay.DAILY,
            )
        )

        expected_stays.append(self.stay_for(user=self.recipient, name="Munich"))

        nodes = routing.find_route(self.packet, calculation_date=date.today())
        self.assertIsNotNone(nodes)
        self.assertEqual(expected_stays, self.stays_from_nodes(nodes))

    def test_find_route_once_stays_in_correct_order(self):
        # Make sure that multiple once stays from the same user are after
        # one another, as otherwise people would have to travel into the past.
        expected_stays = []
        expected_stays.append(self.stay_for(user=self.sender, name="Hamburg"))

        intermediate = User.objects.create(
            email="intermediate@turtlemail.app", username="intermediate"
        )
        expected_stays.append(
            self.stay_for(
                user=intermediate,
                name="Hamburg",
                frequency=Stay.ONCE,
                start=date(2024, 2, 1),
                end=date(2024, 2, 10),
            )
        )
        # This is the stay we don't want to see in the route!
        self.stay_for(
            user=intermediate,
            name="Munich",
            frequency=Stay.ONCE,
            start=date(2024, 1, 1),
            end=date(2024, 1, 10),
        )
        expected_stays.append(
            self.stay_for(
                user=intermediate,
                name="Munich",
                frequency=Stay.ONCE,
                start=date(2024, 2, 20),
                end=date(2024, 2, 25),
            )
        )

        expected_stays.append(self.stay_for(user=self.recipient, name="Munich"))

        nodes = routing.find_route(self.packet, calculation_date=date.today())
        self.assertIsNotNone(nodes)
        self.assertEqual(expected_stays, self.stays_from_nodes(nodes))

    def test_impossible_route_no_stays(self):
        route = routing.find_route(self.packet, calculation_date=date.today())
        self.assertEqual(None, route)

    def test_impossible_route_disconnected_stays(self):
        self.stay_for(user=self.sender, name="Hamburg")
        self.stay_for(user=self.sender, name="Berlin")

        self.stay_for(user=self.recipient, name="Bremen")

        self.stay_for(user=self.recipient, name="Munich")

        route = routing.find_route(self.packet, calculation_date=date.today())
        self.assertEqual(None, route)

    def test_find_route_with_inactive_stays_once(self):
        expected_stays = []

        expected_stays.append(
            self.stay_for(
                user=self.sender,
                name="Hamburg",
            )
        )

        # This stay should not be used because it's
        # inactive at the time of calculation.
        self.stay_for(
            user=self.recipient,
            name="Hamburg",
            frequency=Stay.ONCE,
            start=date(2024, 1, 1),
            end=date(2024, 1, 10),
            inactive_until=date(2024, 1, 2),
        )
        expected_stays.append(
            self.stay_for(
                user=self.recipient,
                name="Hamburg",
                frequency=Stay.ONCE,
                start=date(2024, 1, 22),
                end=date(2024, 1, 23),
            )
        )

        nodes = routing.find_route(self.packet, calculation_date=date(2024, 1, 1))
        self.assertIsNotNone(nodes)
        self.assertEqual(expected_stays, self.stays_from_nodes(nodes))


class CalculateRouteStepDatesTestCase(TestCase):
    def setUp(self):
        self.sender = User.objects.create(
            email="sender@turtlemail.app", username="sender"
        )
        self.recipient = User.objects.create(
            email="recipient@turtlemail.app", username="recipient"
        )
        self.packet = Packet.objects.create(
            sender=self.sender, recipient=self.recipient, human_id="test_id"
        )
        self.location = Location.objects.create(
            is_home=False, point=HAMBURG, user=self.sender
        )

    def test_routestep_dates(self):
        other_location = Location.objects.create(
            is_home=False, point=BERLIN, user=self.sender
        )
        stays = [
            Stay.objects.create(
                location=self.location,
                user=self.sender,
                frequency=Stay.ONCE,
                start=date(2024, 5, 30),
                end=date(2024, 5, 31),
            ),
            Stay.objects.create(
                location=other_location,
                user=self.sender,
                frequency=Stay.ONCE,
                start=date(2024, 6, 10),
                end=date(2024, 6, 14),
            ),
            Stay.objects.create(
                location=other_location, user=self.recipient, frequency=Stay.WEEKLY
            ),
        ]

        bounds = routing.calculate_routestep_dates(stays, date(2024, 5, 27))

        self.assertEqual(
            [
                (date(2024, 5, 30), date(2024, 5, 31)),
                (date(2024, 6, 10), date(2024, 6, 14)),
                (date(2024, 6, 12), date(2024, 6, 19)),
            ],
            bounds,
        )

    def test_bounded_routestep_dates_single(self):
        stays = [
            Stay.objects.create(
                location=self.location,
                user=self.sender,
                frequency=Stay.WEEKLY,
            )
        ]

        bounds = routing.calculate_bounded_routestep_dates(
            stays, date(2024, 1, 1), date(2024, 1, 15)
        )

        self.assertEqual([(date(2024, 1, 1), date(2024, 1, 15))], bounds)

    def test_bounded_routestep_dates_two_weekly(self):
        stays = [
            Stay.objects.create(
                location=self.location, user=self.sender, frequency=Stay.WEEKLY
            ),
            Stay.objects.create(
                location=self.location, user=self.sender, frequency=Stay.WEEKLY
            ),
        ]

        bounds = routing.calculate_bounded_routestep_dates(
            stays, date(2024, 1, 1), date(2024, 1, 15)
        )

        self.assertEqual(
            [
                (date(2024, 1, 1), date(2024, 1, 11)),
                (date(2024, 1, 4), date(2024, 1, 15)),
            ],
            bounds,
        )

    def test_bounded_routestep_dates_weekly_daily(self):
        stays = [
            Stay.objects.create(
                location=self.location, user=self.sender, frequency=Stay.WEEKLY
            ),
            Stay.objects.create(
                location=self.location, user=self.sender, frequency=Stay.DAILY
            ),
        ]

        bounds = routing.calculate_bounded_routestep_dates(
            stays, date(2024, 1, 1), date(2024, 1, 9)
        )

        self.assertEqual(
            [
                (date(2024, 1, 1), date(2024, 1, 8)),
                (date(2024, 1, 4), date(2024, 1, 9)),
            ],
            bounds,
        )
