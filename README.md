# turtlemail

A peer-to-peer do-it-together parcel service.

## System requirements

This software is configured to run in a docker container environment. It depends on docker >= 19 only.

A local setup without containers, use of an external database system and an external web proxy is possible, but not supported or documented in this guide.

## Development Environment

```shell
# run server
make dev

# migrate database (requires running server)
make migrate
```

To use the pre-commit hooks, first [install poetry](https://python-poetry.org/docs/#installation). Then, install the pre-commit hooks:
```
poetry run pre-commit install
```

Django commands should generally be executed locally with:

```
./manage [...args]
```

(`./manage` is our shortcut to `pipx run poetry run ./manage.py`)

Django commands are also available in the container but don’t have write
access to the application code. Execute:

```shell
docker compose exec -it backend turtlemailctl [...args]
```

Once the server is started you can access the development environment
on [`localhost:8637`](http://localhost:8637/).

Custom Django configuration settings can be made in the `turtlemail_settings.py`
in the project root. Note: if you’ve started the docker-compose environment this might
have been auto-created as directory – you can safely delete it and restart docker-compose.

### Working with translations

Work with your code as usual, adding or removing translation keys as needed. Afterwards, run `make update-translations` to generate a new `.pot` file and merge it with the existing `.po` files.

### Import sample data

Run `make fixtures` to populate database with sample data.

All sample users use the password **"testpassword"** by default.

You can overwrite the sample data in `initial_data.yaml` with the contents of your local database by running `make dump-fixtures`.

## Versioning

To help with writing Prototypefund "Monday" updates, we can generate a changelog every two weeks by releasing a new version:

```
git fetch --tags
VERSION=$(poetry run git-cliff --bumped-version)
poetry run git-cliff --bump -o CHANGELOG.md
# Update version in pyproject.toml
vim pyproject.toml
git add .
git commit -m "bump: Release $VERSION"
git tag $VERSION
git push
git push --tags
```

This will update the version in `pyproject.toml`, **create a new commit**, add a tag to that commit, and re-generate `CHANGELOG.md`.

See [the commitizen bump docs](https://commitizen-tools.github.io/commitizen/bump/) for more info.

## Deployment

turtlemail can be deployed from source and via a container image.
Only container image deployments are tested in production.
We encourage you to use podman as container executor.

### Container Image

A docker and podman compatible container image is provided at
`git-registry.hack-hro.de:443/turtlemail/turtlemail:rolling`.

Administrators should bind a volume or filesystem path to `/var/lib/turtlemail`,
which is used as directory for dynamic data. Data is stored with uid/gid 400/400.

### Web server

We have only tested NGINX in production.

You can find example configuration files in
[docker/nginx-app.conf](./docker/nginx-app.conf) and
[docker/nginx-server.conf](./docker/nginx-server.conf).

### Application environment variables

turtlemail mostly uses environment variables for configuration.
Environment variables marked with ❗ must be set.
Those marked with 👀 should at least be inspected.

`DATA_DIR` 👀
: A directory path that is used as storage for dynamic data.

`SECRET_KEY` ❗
: A password-like string with high entropy. This is used to encrypt sessions.

`DEBUG`
: Enable debug mode by setting this to `yes`.

`ALLOWED_HOSTS` ❗
: The hostname turtlemail operates under (e.g. `turtlemail.example.org`).
Multiple entries can be separated with a comma.

`CSRF_TRUSTED_ORIGINS`
: Trusted origins for CSRF tokens (including protocol and port,
like `https://turtlemail.example.org`).
Defaults to the list of allowed hosts above prefixed with `https://`.

`DATABASE_URL` ❗
: Database URL for accessing the database.
Format is specified in the
[dj_database_url documentation](https://pypi.org/project/dj-database-url/#url-schema).
Be advised that we only officially support PostgreSQL and SQLite.

`EMAIL_DEFAULT_FROM` 👀
: Default mail address for the `From` header used in emails sent by turtlemail.

`EMAIL_SMTP` 👀
: The mail server used to send emails. Must be specified as a URL.
Examples:
`smtp+tls://user:pw@mail.example.org:465?timeout=10`
`smtp+starttls://user:pw@mail.example.org:587`

`SESSION_TIMEOUT_SECONDS` 👀
: Controls the lifetime of a session. Defaults to 2 weeks.
If you want users to be logged out faster, change it to a lower value
(e.g. `86400` for a day).

`ENVIRONMENT` 👀
: A custom free-form environment name, used in debugging messages.

`SENTRY_DSN` 👀
: A Sentry DSN URL that can be used to collect error reports.

### Application server environment variables

turtlemail uses [uvicorn](https://www.uvicorn.org/) as application server.
uvicorn comes with a multitude of configuration options, a few of which
can be set with environment variables.

This includes:

`FORWARDED_ALLOW_IPS` 👀
: Controls trusted proxies allowed to proxy traffic to the application server.

`WEB_CONCURRENCY` 👀
: Controls the number of workers used to handle incoming requests. Defaults
to `1`. You likely want to increase this.

See the [uvicorn settings documentation](https://www.uvicorn.org/settings/) for
further and more extensive information.

### Django Python configuration

You can put a custom Django configuration with the name `settings.py`
in `/etc/turtlemail` on the filesystem. It will be loaded automatically.
