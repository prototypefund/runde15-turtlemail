import datetime
import enum
import json
import logging
import os
from pathlib import Path
import socket
from typing import Optional, Sequence

from django.conf import settings
from django.contrib.staticfiles.storage import staticfiles_storage

logger = logging.getLogger(__name__)
static = staticfiles_storage.url


class CachedManifest:
    def __init__(self, path: Path):
        self._path = path
        self._value = None
        self._last_update = datetime.datetime.now()

    @property
    def exists(self):
        return self._path.exists()

    def _should_update(self):
        if self._value is None:
            return True
        if settings.DEBUG:
            return os.stat(self._path).st_mtime > self._last_update.timestamp()
        return False

    def get(self) -> dict:
        if self._should_update():
            with open(self._path) as manifest:
                self._value = json.load(manifest)
        return self._value


_MANIFEST = CachedManifest(settings.VITE_MANIFEST)


class AssetSource(enum.Enum):
    LIVE_SERVER = "live-server"
    MANIFEST = "manifest"
    DISABLED = "disabled"
    AUTO_DETECT = "auto-detect"

    @classmethod
    def parse(cls, asset_source: Optional[str]) -> "AssetSource":
        if asset_source is None:
            return cls.AUTO_DETECT
        return cls(asset_source)

    @classmethod
    def choices(cls) -> Sequence[str]:
        return tuple(s.value for s in cls)


def _is_port_open(port: int, host: str = "localhost") -> bool:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            return sock.connect_ex((host, port)) == 0
    except socket.gaierror:
        logger.warning("Could not resolve host '%s'.", host)
        return False


def _determine_asset_source() -> AssetSource:
    is_vite_port_open = _is_port_open(settings.VITE_PORT, settings.VITE_HOST)
    manifest_exists = _MANIFEST.exists

    try:
        asset_source = AssetSource.parse(settings.ASSET_SOURCE)
    except ValueError:
        choices = ", ".join(f"`{name}`" for name in AssetSource.choices())
        raise ValueError(
            f"ASSET_SOURCE should be {choices}, or undefined (`None`).",
        )

    if asset_source is AssetSource.MANIFEST:
        if not manifest_exists:
            raise RuntimeError(
                "You’ve requested to use the asset manifest by setting the ASSET_SOURCE "
                "setting to `manifest` but no asset manifest has been generated. "
                "Did you forget to run `npm run build`?"
            )
        return asset_source
    elif asset_source is AssetSource.LIVE_SERVER:
        if not is_vite_port_open:
            logger.warning(
                "You’ve requested to use the Vite dev server by setting the ASSET_SOURCE "
                "setting to `live-server` but the server did not (yet?) start. "
                "Be sure to run `npm run dev` if you rely on assets served from the Vite server."
            )
        return asset_source
    elif asset_source is AssetSource.DISABLED:
        return asset_source

    assert (
        asset_source is AssetSource.AUTO_DETECT
    ), "Only asset source auto-detection should be left to handle."
    # handle auto-detection
    if is_vite_port_open:
        return AssetSource.LIVE_SERVER
    elif manifest_exists:
        return AssetSource.MANIFEST
    elif settings.DEBUG is True:
        logger.warning(
            "No Vite dev server or asset manifest was found. "
            "Using Vite dev server hoping you will start one with `npm run dev`."
        )
        return AssetSource.LIVE_SERVER
    else:
        raise RuntimeError("No Vite dev server or asset manifest was found.")


def _prefix(asset):
    return f"turtlemail/bundled/{asset}"


def _stylesheet(asset_url: str, prefix=True):
    url = static(_prefix(asset_url)) if prefix else asset_url
    return f"<link rel='stylesheet' href='{url}'>"


def _script(asset_url: str, prefix=True):
    url = static(_prefix(asset_url)) if prefix else asset_url
    return f"<script type='module' src='{url}'></script>"


def get_asset_html(entrypoint: str | None = None):
    entrypoint = entrypoint if entrypoint is not None else settings.VITE_ENTRYPOINT

    def _gen():
        asset_source = _determine_asset_source()
        host = settings.VITE_PUBLIC_HOST
        port = settings.VITE_PORT
        if asset_source is AssetSource.LIVE_SERVER:
            origin = f"http://{host}:{port}"
            yield _script(f"{origin}/{entrypoint}", prefix=False)
        elif asset_source is AssetSource.MANIFEST:
            manifest = _MANIFEST.get()
            main = manifest[entrypoint]
            file = main["file"]
            yield _stylesheet(file) if file.endswith(".css") else _script(file)
            if "css" in main:
                for style in main["css"]:
                    yield _stylesheet(style)

    return "\n".join(_gen())
