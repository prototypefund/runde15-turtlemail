from django.utils.safestring import mark_safe
from django_jinja import library

from turtlemail.base.vite import get_asset_html


@library.global_function
def vite_assets(entrypoint: str):
    return mark_safe(get_asset_html(entrypoint))
