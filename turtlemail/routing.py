from dataclasses import dataclass
from datetime import date, timedelta
import logging
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
    earliest_estimated_handover: Tuple[date, date]
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
    stay: Stay, visited_stay_ids: Set[int]
) -> models.QuerySet[Stay]:
    once_time_overlaps = models.Value(True)
    # TODO take estimated handover dates into account here
    # to make sure we don't get a ONCE stay that's e.g. in the past
    if stay.start is not None and stay.end is not None:
        once_time_overlaps = models.Q(
            start__lte=stay.end,
            end__gte=stay.start,
        )
    time_matches = ~models.Q(frequency=Stay.ONCE) | once_time_overlaps
    is_near_location = models.Q(
        location__point__distance_lte=(stay.location.point, RADIUS),
    )
    is_from_same_user = models.Q(user__id=stay.user.id)
    is_unvisited = ~models.Q(id__in=visited_stay_ids)
    is_other_stay = ~models.Q(id=stay.id)
    return Stay.objects.filter(
        # TODO multiple "once" stays from the same user should be after one another
        (time_matches & is_near_location) | is_from_same_user,
        is_unvisited,
        is_other_stay,
    )


# Based on this function, the algorithm decides where to look first.
# Stays with earlier handover dates are considered first.
# Handover dates are always estimated, even if every stay along the route
# has fixed dates. We don't know when people will actually meet.
def get_estimated_handover_range(
    previous_handover: Tuple[date, date], next_stay: Stay
) -> Tuple[date, date]:
    earliest, latest = previous_handover
    match next_stay.frequency:
        case Stay.DAILY:
            return (
                earliest + timedelta(days=1),
                latest + timedelta(days=2),
            )
        case Stay.WEEKLY:
            return (earliest + timedelta(days=1), latest + timedelta(days=7))
        case Stay.ONCE if next_stay.start is not None and next_stay.end is not None:
            return (max(earliest, next_stay.start), min(latest, next_stay.end))
        case _:
            return (earliest + timedelta(days=14), latest + timedelta(days=30))


# This is the main algorithm.
def find_route(packet: Packet) -> List[RoutingNode] | None:
    # TODO check for correct packet state before finding route
    # e.g. don't calculate a new route for a packet that already has a
    # valid route

    # Set up initial data

    # We'll start by picking an arbitrary stay of the packet sender
    # TODO: find out were they're likely staying right now and use
    # that as a starting point
    starting_stays = packet.sender.stay_set.all()
    if len(starting_stays) == 0:
        return None

    starting_stay = min(
        starting_stays,
        key=lambda stay: get_estimated_handover_range(
            (starting_date, starting_date), stay
        ),
    )
    if starting_stay is None:
        return None

    # This is the data structure our algorithm uses to keep track of
    # calculcated "distances". In our case, "distance" means "how early
    # can we deliver the packet via this stay?".
    # One routing node is always associated with one stay, and vice versa.
    starting_node = RoutingNode(
        stay=starting_stay,
        earliest_estimated_handover=(
            packet.created_at.date(),
            packet.created_at.date(),
        ),
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
        reachable_stays = get_reachable_stays(current_node.stay, visited_stay_ids)
        logger.debug("- visiting %s, reachable stays:", current_node.stay)
        for stay in reachable_stays:
            # For each of the neighbors, calculcate how quick we could
            # reach them
            earliest_handover = get_estimated_handover_range(
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
                "%s %s, previous node: %s",
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

    logger.debug("Found a route with %s steps", len(reverse_route))

    return list(reversed(reverse_route))


def create_new_route(packet: Packet) -> Route | None:
    try:
        with transaction.atomic():
            nodes = find_route(packet)
            if nodes is None:
                DeliveryLog.objects.create(
                    packet=packet, action=DeliveryLog.NO_ROUTE_FOUND
                )
                return None

            route = Route.objects.create(status=Route.CURRENT, packet=packet)

            DeliveryLog.objects.create(
                packet=packet, route=route, action=DeliveryLog.NEW_ROUTE
            )

            steps = []
            previous_step = None
            for node in nodes:
                step = RouteStep.objects.create(
                    stay=node.stay,
                    start=node.earliest_estimated_handover[0],
                    end=node.earliest_estimated_handover[1],
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
