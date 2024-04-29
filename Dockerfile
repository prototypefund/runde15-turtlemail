FROM node:lts-alpine as assets
USER root
RUN apk add coreutils make
WORKDIR /home/node
ADD package.json package-lock.json ./
RUN npm ci
ADD postcss.config.js tailwind.config.js tsconfig.json vite.config.ts Makefile ./
ADD src/ ./src/
ADD turtlemail/ ./turtlemail/
RUN make assets


FROM debian:bookworm as base

ARG build_version

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV POETRY_VIRTUALENVS_OPTIONS_SYSTEM_SITE_PACKAGES=true
ENV POETRY_VIRTUALENVS_IN_PROJECT=true
ENV LANG C.UTF-8

ENV PYTHONPATH=/usr/share/turtlemail
ENV DJANGO_SETTINGS_MODULE=turtlemail.settings
ENV DATA_DIR=/var/lib/turtlemail
ENV ASSET_SOURCE=manifest
ENV RELEASE=${build_version}

RUN apt update -y && \
    apt install -y --no-install-recommends \
      adduser  \
      gettext \
      locales \
      netcat-openbsd \
      postgresql-client \
      uvicorn \
      python3 \
      python3-poetry \
      python3-psycopg2 \
      # GeoDjango Dependencies
      binutils \
      libproj-dev \
      gdal-bin \
      && \
    apt-get clean -y && \
    rm -rf /var/lib/apt/lists/*
ADD pyproject.toml poetry.lock /usr/share/turtlemail/
RUN poetry --directory /usr/share/turtlemail/ install --sync --without=dev --with=production --no-root \
    && sed -i 's/include-system-site-packages = false/include-system-site-packages = true/' "$(poetry --directory /usr/share/turtlemail/ env info --path)/pyvenv.cfg"
ADD turtlemail /usr/share/turtlemail/turtlemail/
COPY --from=assets /home/node/turtlemail/static/turtlemail/bundled /usr/share/turtlemail/turtlemail/static/turtlemail/bundled/
COPY docker/entrypoint.sh /usr/local/bin/turtlemailctl
RUN printf 'de_DE.UTF-8 UTF-8\nen_US.UTF-8 UTF-8\n' >/etc/locale.gen && \
    locale-gen && \
    update-locale LANG=de_DE.UTF-8 LC_MESSAGES=en_US.UTF-8
RUN turtlemailctl compilemessages --locale de >/dev/null

RUN adduser --system --group --firstuid 400 --firstgid 400 --home /var/lib/turtlemail _turtlemail && chown -R _turtlemail: /var/lib/turtlemail
WORKDIR /var/lib/turtlemail
EXPOSE 8000
ENTRYPOINT ["/usr/local/bin/turtlemailctl"]
CMD ["uvicorn", "0.0.0.0:8000"]
HEALTHCHECK --start-period=20s CMD nc -z localhost 8000


FROM base as dev
RUN poetry --directory /usr/share/turtlemail/ run pip3 install 'pydevd-pycharm'
EXPOSE 28472
USER _turtlemail


FROM base as production
USER _turtlemail
