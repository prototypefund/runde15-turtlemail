from huey import crontab
from huey.contrib.djhuey import periodic_task, task


# tbd: tasks for testing queues. Will be removed
@task()
def count_beans(number):
    print("-- counted %s beans --" % number)
    return "Counted %s beans" % number


@periodic_task(crontab(minute="*/1"))
def every_five_mins():
    print("Every five minutes this will be printed by the consumer")
