import functools
import inspect

from asgiref.sync import sync_to_async
import django.db


def ensure_database_connection(func):
    """ensure a usable database connection before every single request

    See https://code.djangoproject.com/ticket/32589
    Long-running management commands are expected to close old/unusable
    connections from time to time.
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        django.db.close_old_connections()
        try:
            return func(*args, **kwargs)
        finally:
            django.db.close_old_connections()

    if inspect.iscoroutine(func):
        return sync_to_async(wrapper)
    else:
        return wrapper
