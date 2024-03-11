import urllib.parse

from django.core.mail.backends.smtp import EmailBackend as SMTPEmailBackend


class EmailBackend(SMTPEmailBackend):
    def __init__(self, **kwargs):
        from django.conf import settings

        url = urllib.parse.urlparse(settings.EMAIL_BACKEND_URL)
        query = urllib.parse.parse_qs(url.query)

        kwargs.setdefault("host", url.hostname)
        kwargs.setdefault("port", url.port)
        kwargs.setdefault("username", url.username)
        kwargs.setdefault("password", url.password)
        kwargs.setdefault("use_tls", url.scheme == "smtp+starttls")
        kwargs.setdefault("use_ssl", url.scheme == "smtp+tls")

        if timeout := query.get("timeout", None):
            kwargs.setdefault("timeout", int(timeout[0]))
        elif timeout := getattr(settings, "EMAIL_TIMEOUT", None):
            kwargs.setdefault("timeout", int(timeout))

        super().__init__(**kwargs)
