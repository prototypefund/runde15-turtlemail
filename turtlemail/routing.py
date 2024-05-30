from dataclasses import dataclass
from datetime import date, timedelta
import logging
import math
from typing import List, Set, Tuple
from django.contrib.gis import measure
from django.db import models, transaction
from turtlemail.models import DeliveryLog, Packet, Route, RouteStep, Stay

RADIUS = measure.Distance(km=10)
# Only allow routes that take less than this time to complete.
MAX_ROUTE_LENGTH = timedelta(days=60)

logger = logging.getLogger(__name__)

# Design thoughts:
# I would have preferred an algorithm that doesn't perform database
# queries but purely transforms input data into a result.
# But to be able to handle lots of users and their stays,
# it would be problematic to load all stays from the database at once.
# So, I've decided to query for connections between stays inside the algorithm.

# The algorithm is loosely modeled after Dijkstra's pathfinding algorithm:
# https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm


# This is the data structure we use to keep track of the dates
# we calculate for each possible route.
@dataclass
class RoutingNode:
    # Best discovered handover date yet.
    # We'll use this to find the fastest route once the algorithm
    # completes.
    # Note: we compare these tuples in some places. How does this work?
    # Python compares the first dates of both tuples, and only if they
    # are equal, it compares the second dates.
    earliest_estimated_handover: date
    # The next step on the shortest way to the source node.
    previous_node: "RoutingNode | None"
    # We use this at the end of the algorithm to return
    # a list of stays that make up the route.
    stay: Stay

    def __hash__(self) -> int:
        return self.stay.id


# Here, we "discover" new stays for the algorithm to look at.
# Given an origin stay, we build a query for finding other stays
# where the delivery could be handed over to another person.
def get_reachable_stays(
    stay: Stay, visited_stay_ids: Set[int], calculation_date: date
) -> models.QuerySet[Stay]:
    time_matches = models.Q(models.Value(True))
    # TODO take estimated handover dates into account here
    # to make sure we don't get a ONCE stay that's
    # earlier than the previous handover dates
    # TODO multiple "once" stays from the same user should be after one another
    if stay.start is not None and stay.end is not None:
        # The previous stay is limited to a certain
        # date range.
        # Make sure we only select stays matching this
        # range.
        time_matches = ~models.Q(frequency=Stay.ONCE) | models.Q(
            start__lte=stay.end, end__gte=stay.start
        )

    is_near_location = models.Q(
        location__point__distance_lte=(stay.location.point, RADIUS),
    )
    is_from_same_user = models.Q(user__id=stay.user.id)
    is_unvisited = ~models.Q(id__in=visited_stay_ids)
    is_other_stay = ~models.Q(id=stay.id)
    is_active = models.Q(inactive_until__isnull=True) | models.Q(
        inactive_until__lt=calculation_date
    )
    not_deleted = models.Q(deleted=False)
    return Stay.objects.filter(
        (time_matches & is_near_location) | is_from_same_user,
        is_unvisited,
        is_other_stay,
        is_active,
        not_deleted,
    )


# Based on this function, the algorithm decides where to look first.
# Stays with earlier handover dates are considered first.
# Handover dates are always estimated, even if every stay along the route
# has fixed dates. We don't know when people will actually meet.
def get_earliest_estimated_handover(previous_handover: date, next_stay: Stay) -> date:
    earliest = previous_handover
    match next_stay.frequency:
        case Stay.DAILY:
            return earliest + timedelta(days=1)

        case Stay.WEEKLY:
            return earliest + timedelta(days=3)
        case Stay.ONCE if next_stay.start is not None:
            return max(earliest, next_stay.start)
        case _:
            return earliest + timedelta(days=14)


def get_starting_stay(packet: Packet, calculation_date: date) -> Stay | None:
    # We'll pick the stay of the sender
    # that's closest to the current date
    is_active = models.Q(inactive_until__isnull=True) | models.Q(
        inactive_until__lt=calculation_date
    )
    time_matches = ~models.Q(frequency=Stay.ONCE) | models.Q(end__gte=calculation_date)
    starting_stays = packet.sender.stay_set.filter(is_active, time_matches).all()
    if len(starting_stays) == 0:
        return None

    return min(
        starting_stays,
        key=lambda stay: get_earliest_estimated_handover(calculation_date, stay),
    )


# This is the main algorithm.
def find_route(packet: Packet, calculation_date: date) -> List[RoutingNode] | None:
    # Set up initial data
    starting_stay = get_starting_stay(packet, calculation_date)
    if starting_stay is None:
        return None

    # This is the data structure our algorithm uses to keep track of
    # calculcated "distances". In our case, "distance" means "how early
    # can we deliver the packet via this stay?".
    # One routing node is always associated with one stay, and vice versa.
    starting_handover_date = get_earliest_estimated_handover(
        calculation_date, starting_stay
    )
    starting_node = RoutingNode(
        stay=starting_stay,
        earliest_estimated_handover=starting_handover_date,
        previous_node=None,
    )

    # We don't want to load *all* stays from the database, only
    # those that are reachable from our sender.
    # For new routing nodes, we check if they already were visited
    # through another route by looking into this dictionary.
    routing_nodes_by_stay_id = {starting_node.stay.id: starting_node}

    # When looking for new Stays to load from the database, exclude
    # the stays we already visited.
    visited_stay_ids = set()

    nodes_to_visit = {starting_node}

    current_node = starting_node

    # Start searching!
    # We search until we've either found a route to our recipient,
    # or until we can't find any more stays that are reachable.
    while len(nodes_to_visit) > 0:
        # find next node to visit by looking at the earliest possible
        # estimated handover date
        current_node = min(
            nodes_to_visit, key=lambda node: node.earliest_estimated_handover
        )

        if current_node.stay.user.id == packet.recipient.id:
            # We've found the shortest route to the target!
            break

        # Find neighbors of the node we're visiting
        reachable_stays = get_reachable_stays(
            current_node.stay, visited_stay_ids, calculation_date
        )
        logger.debug("- visiting %s, reachable stays:", current_node.stay)
        for stay in reachable_stays:
            # For each of the neighbors, calculcate how quick we could
            # reach them
            earliest_handover = get_earliest_estimated_handover(
                current_node.earliest_estimated_handover, stay
            )

            latest_allowed_handover = calculation_date + MAX_ROUTE_LENGTH
            if earliest_handover > latest_allowed_handover:
                # Reaching this node through this route takes too long.
                # For this search, we consider it unreachable.
                continue

            # If we've loaded this stay from the db for the first time,
            # Create a RoutingNode for it, and make sure we'll visit it later.
            routing_node = routing_nodes_by_stay_id.get(stay.id)
            if routing_node is None:
                routing_node = RoutingNode(
                    stay=stay,
                    earliest_estimated_handover=earliest_handover,
                    previous_node=current_node,
                )
                routing_nodes_by_stay_id[stay.id] = routing_node
                nodes_to_visit.add(routing_node)

            logger.debug(
                "%s (handover: %s), previous node: %s",
                stay,
                routing_node.earliest_estimated_handover,
                routing_node.previous_node.stay
                if routing_node.previous_node is not None
                else None,
            )

            # We might have reached this node through a different route
            # before. Check if the route we're currently on is faster
            # than the previous one.
            if earliest_handover < routing_node.earliest_estimated_handover:
                # We've discovered a faster route to this node!
                # Update its estimated handover date and the pointer
                # to the previous node, to remember that it's the fastest
                # way to get here.
                logger.debug("updating earliest handover date: %s", earliest_handover)
                routing_node.earliest_estimated_handover = earliest_handover
                routing_node.previous_node = current_node

        # mark node as visited
        visited_stay_ids.add(current_node.stay.id)
        nodes_to_visit.remove(current_node)

    logger.debug("finished calculating distances")

    if current_node.stay.user.id != packet.recipient.id:
        # We've visited all reachable nodes but were unable to
        # find a route to the recipient
        logger.debug("Found no route to recipient")
        return None

    # We've found the target. Reconstruct the shortest route
    # from the nodes we've visited.
    reverse_route = []
    next_node = current_node

    while next_node is not None:
        reverse_route.append(next_node)
        next_node = next_node.previous_node

    route = list(reversed(reverse_route))

    route = trim_sender_stays_at_start(route)

    logger.debug("Found a route with %s steps", len(reverse_route))

    return route


def trim_sender_stays_at_start(
    route: List[RoutingNode],
) -> List[RoutingNode]:
    """
    We don't want routes to start with multiple of the sender's stays:

    - We don't actually know where the packet is at the moment
    - It's confusing to senders

    So we remove these stays from the start of any route we calculate.
    """
    if len(route) == 0:
        return route

    sender = route[0].stay.user
    new_starting_node_index = 0
    # Iterate the start of the route until we hit the end of
    # the stays belonging to our sender.
    for i, node in enumerate(route):
        if node.stay.user == sender:
            new_starting_node_index = i
        else:
            break

    return route[new_starting_node_index:]


def middle_of_date_range(date_range: Tuple[date, date]) -> date:
    return date_range[0] + (date_range[1] - date_range[0]) / 2


def calculate_routestep_dates(
    stays: List[Stay], calculation_date: date
) -> List[Tuple[date, date]]:
    """
    Determine concrete date ranges for all stays.
    Propose some dates for flexible stays that don't have fixed dates set,
    in a way that all route steps have some overlap for exchanging packets.
    Keep dates for stays that already have fixed dates.
    """
    # TODO handle consecutive stays belonging to the same user
    result = []

    if len(stays) == 0:
        return result

    start = calculation_date
    stays_that_need_dates = []
    for stay in stays:
        if stay.start is None or stay.end is None:
            # remember this until we find the next ONCE stay.
            stays_that_need_dates.append(stay)
        else:
            # Calculcate dates for previous flexible stays
            middle = middle_of_date_range((stay.start, stay.end))
            result = result + calculate_bounded_routestep_dates(
                stays_that_need_dates, start, middle
            )
            # Keep the dates from this stay as well.
            result.append((stay.start, stay.end))

            # Calculate dates for the next stays starting
            # at the middle of this stay.
            stays_that_need_dates = []
            start = middle

    if len(stays_that_need_dates) > 0:
        result = result + calculate_bounded_routestep_dates(
            stays_that_need_dates, start, None
        )

    return result


def ideal_day_length(stay: Stay) -> float:
    match stay.frequency:
        case Stay.DAILY:
            return 1
        case Stay.WEEKLY:
            return 7
        case Stay.SOMETIMES:
            return 28
        case Stay.ONCE:
            raise Exception("this function is not designed for stays with fixed dates.")
        case _:
            raise Exception("unsupported stay type")


def calculate_bounded_routestep_dates(
    stays: List[Stay], start_bound: date, end_bound: date | None
) -> List[Tuple[date, date]]:
    """
    Given
    - a list of Stays that are *not* ONCE stays (meaning they don't have fixed start and end dates),
    - inclusive start and end dates,

    return one date range for each stay, so that all of the ranges fit within the given start and end date.
    The date ranges will overlap, so people can meet and exchange packets
    from one stay to the next.
    """

    sum_of_weights = sum([ideal_day_length(stay) for stay in stays])
    if end_bound is None:
        end_bound = start_bound + timedelta(days=sum_of_weights)
    available_days = (end_bound - start_bound).days

    non_overlapping_ranges = []
    next_stay_start = start_bound
    # First, calculate ranges according to the weights, but don't let them overlap.
    for stay in stays:
        days_for_this_stay = math.floor(
            available_days * ideal_day_length(stay) / sum_of_weights
        )
        next_stay_end = next_stay_start + timedelta(days=days_for_this_stay)
        non_overlapping_ranges.append((next_stay_start, next_stay_end))
        next_stay_start = next_stay_end

    if len(non_overlapping_ranges) < 2:
        return non_overlapping_ranges

    # Then, move the ranges so they overlap.
    final_ranges = []

    for i, (start, end) in enumerate(non_overlapping_ranges):
        overlapping_start = start
        if i - 1 >= 0:
            overlapping_start = middle_of_date_range(non_overlapping_ranges[i - 1])
        overlapping_end = end
        if i + 1 < len(non_overlapping_ranges):
            next_range = non_overlapping_ranges[i + 1]
            overlapping_end = middle_of_date_range(next_range)

        final_ranges.append((overlapping_start, overlapping_end))

    return final_ranges


def create_new_route(packet: Packet, starting_date: date) -> Route | None:
    try:
        with transaction.atomic():
            nodes = find_route(packet, starting_date)
            if nodes is None:
                DeliveryLog.objects.create(
                    packet=packet, action=DeliveryLog.NO_ROUTE_FOUND
                )
                return None

            route = Route.objects.create(status=Route.CURRENT, packet=packet)

            DeliveryLog.objects.create(
                packet=packet, route=route, action=DeliveryLog.NEW_ROUTE
            )

            step_dates = calculate_routestep_dates(
                [node.stay for node in nodes], calculation_date=starting_date
            )
            steps = []
            previous_step = None
            for node, (start, end) in zip(nodes, step_dates, strict=True):
                step = RouteStep.objects.create(
                    stay=node.stay,
                    start=start,
                    end=end,
                    previous_step=previous_step,
                    next_step=None,
                    packet=packet,
                    route=route,
                    status=RouteStep.SUGGESTED,
                )

                steps.append(step)
                previous_step = step

            next_step = None
            for step in reversed(steps):
                if next_step is not None:
                    step.next_step = next_step
                    step.end = next_step.start

                next_step = step

            RouteStep.objects.bulk_update(steps, ["next_step"])

            return route
    except Exception as e:
        logger.error(e)
        DeliveryLog.objects.create(packet=packet, action=DeliveryLog.NO_ROUTE_FOUND)


def check_and_recalculate_route(route: Route, starting_date: date) -> Route | None:
    status = route.packet.status()

    if status != Packet.Status.ROUTE_OUTDATED:
        # everything's fine
        return route

    logger.info("Route %s is outdated. Looking for a new one", route)

    # We need a new route!
    # TODO handle packets that have already completed some route steps
    route.status = Route.CANCELLED
    route.save()
    return create_new_route(route.packet, starting_date)
