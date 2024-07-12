import os
import django
from jinja2.ext import babel_extract as jinja_babel_extract

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "turtlemail.settings")
django.setup()


def babel_extract(fileobj, keywords, comment_tags, options):
    from django.template import engines

    options["extensions"] = ",".join(
        engines.templates["jinja"]["OPTIONS"]["extensions"]
    )
    return jinja_babel_extract(fileobj, keywords, comment_tags, options)
