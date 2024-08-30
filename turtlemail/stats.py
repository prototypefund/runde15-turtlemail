from typing import TypedDict
import statistics

from django.db.models import Q, Min, Max, Count
from turtlemail.models import User, Packet, RouteStep


class StayStats(TypedDict):
    min: int
    max: int
    median: float


class PackageStats(TypedDict):
    waiting: int
    in_transit: int
    delivered: int


class AccountStats(TypedDict):
    total_number: int


def get_account_stats() -> AccountStats:
    return {
        "total_number": User.objects.all().count(),
    }


def get_stay_stats() -> StayStats:
    users = User.objects.annotate(
        stay_count=Count("stay", filter=Q(stay__deleted=False))
    )
    stays = users.aggregate(min=Min("stay_count"), max=Max("stay_count"))
    return {
        "min": stays["min"],
        "max": stays["max"],
        "median": statistics.median(users.values_list("stay_count", flat=True)),
    }


def get_packet_stats() -> PackageStats:
    # TODO: needs tests
    no_route_packets = Packet.objects.without_valid_route()
    packets_with_route = Packet.objects.exclude(
        id__in=no_route_packets.values_list("id", flat=True)
    )
    completed_route_steps = RouteStep.objects.filter(
        status=RouteStep.COMPLETED
    ).values_list("id", flat=True)
    delivered_packets = packets_with_route.filter(
        all_routes__steps__in=completed_route_steps
    ).distinct()
    delivered_packets_count = delivered_packets.count()

    return {
        "waiting": no_route_packets.count(),
        "in_transit": packets_with_route.count() - delivered_packets_count,
        "delivered": delivered_packets_count,
    }
