import datetime
from logging import debug
from huey import crontab
from huey.contrib.djhuey import periodic_task, lock_task
from turtlemail.models import Packet
from turtlemail.routing import recalculate_missing_routes


@periodic_task(crontab(minute="*/1"))
@lock_task("recalculate_missing_routes")
def every_minute():
    packets = Packet.objects.without_valid_route()
    debug("Found %d packets for recalculating routes", len(packets))
    recalculate_missing_routes(packets, datetime.datetime.now(datetime.UTC))
