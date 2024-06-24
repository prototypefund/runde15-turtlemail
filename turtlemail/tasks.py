from huey import crontab
from huey.contrib.djhuey import periodic_task


@periodic_task(crontab(minute="*/1"))
def every_minute():
    print("Every minute this message will be printed by the consumer")
