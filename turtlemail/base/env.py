# ! This file is used in settings and should not contain any code
# ! that interferes with django’s initialization (e.g. model imports)

import os
import typing
import urllib.parse


class _Undefined:
    pass


def get_env(env_var_name: str, *, cast=str, default: typing.Any = _Undefined):
    try:
        return cast(os.environ[env_var_name])
    except KeyError:
        if default is not _Undefined:
            return default
        raise


def get_env_list(env_var_name: str, *, separator=",", cast=str, default: typing.Any = _Undefined):
    try:
        value = get_env(env_var_name)
    except KeyError:
        return default if default is not _Undefined else []
    split_env = [v.strip() for v in value.split(separator)]
    return [cast(v) for v in split_env if v]


def is_env_true(env_var_name, *, default: bool = False):
    try:
        return os.environ[env_var_name].lower() in {"1", "yes", "on", "true"}
    except KeyError:
        return default


def get_env_address(env_var_name, *, default: tuple[str | None, int | None] | _Undefined = _Undefined):
    try:
        raw_address: str | None = get_env(env_var_name)
    except KeyError:
        if default is not _Undefined:
            return default
        raise
    raw_address_parts = raw_address.rsplit(":", 1)
    if len(raw_address_parts) == 1:
        return raw_address, None
    elif len(raw_address_parts) == 2:
        host, port = raw_address_parts
        return host, int(port)
    else:
        raise ValueError("Unknown address format")


def parse_channel_layers(env_var_name: str, default=None):
    env_var = get_env(env_var_name, default=default)
    if env_var is None:
        return {}

    def mkconf(backend: str, config: dict | None = None):
        conf = {"BACKEND": backend}
        if config:
            conf["CONFIG"] = config
        return {"default": conf}

    url = urllib.parse.urlparse(env_var)

    if url.scheme == "memory":
        return mkconf("channels.layers.InMemoryChannelLayer")

    if url.scheme == "redis":
        return mkconf("channels_redis.core.RedisChannelLayer", {"hosts": [env_var]})

    raise ValueError(f"Invalid channel layer config: {env_var}")
