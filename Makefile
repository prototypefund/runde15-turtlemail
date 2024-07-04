DIR_BUILD ?= build
DIR_SRC = src

NODE_MODULES = node_modules
NODE ?= node
NPM ?= npm
NPX ?= npx
ESLINT ?= $(NODE_MODULES)/.bin/eslint
DOCKER ?= $(shell command -v docker)
COMPOSE ?= $(shell command -v docker-compose || echo "$(DOCKER) compose")

OUTPUT_DIR ?= turtlemail/static/turtlemail/bundled/
OUTPUT_ASSET_MANIFEST = $(OUTPUT_DIR)/.vite/manifest.json

DEPS_ASSETS = $(shell find "$(DIR_SRC)" -type f)

define help_message =
dev:          start dev environment
migrate:      migrate database (in dev environment)
build:        build app dependencies
update-translations: Update .po files
endef

.PHONY: help
help:
	@$(info $(help_message)):

.PHONY: build
build: assets

$(NODE_MODULES): package.json package-lock.json
	ADBLOCK=true "$(NPM)" ci --no-progress
	"$(NPX)" --yes -- update-browserslist-db@latest
	@touch --no-create "$(NODE_MODULES)"

$(ESLINT): $(NODE_MODULES)

$(OUTPUT_ASSET_MANIFEST): $(NODE_MODULES) $(DEPS_ASSETS)
	"$(NPM)" run build

.PHONY: clean
clean:
	rm -rf \
			.tox \
			.coverage \
			"$(NODE_MODULES)" \
			"$(OUTPUT_DIR)"

.PHONY: assets
assets: $(OUTPUT_ASSET_MANIFEST)

.PHONY: dev
dev:
	COMPOSE_FILE=docker-compose.yml:docker-compose.dev.yml $(COMPOSE) up --build --force-recreate

.PHONY: migrate
migrate:
	$(COMPOSE) exec -it backend turtlemailctl migrate

.PHONY: makemigrations
makemigrations:
	$(COMPOSE) exec --user root backend turtlemailctl makemigrations
	poetry run ruff format turtlemail/migrations

.PHONY: update-translations
update-translations:
	poetry run pybabel extract -F babel.cfg -o turtlemail/locale/django.pot --no-location .
	poetry run pybabel update -i turtlemail/locale/django.pot --domain django --output-dir turtlemail/locale --ignore-pot-creation-date
	# Remove extra newline at end of file to make pre-commit checks happy
	truncate -s -1 turtlemail/locale/de/LC_MESSAGES/django.po
	rm turtlemail/locale/django.pot
	./manage compilemessages

.PHONY: fixtures
fixtures: migrate
	$(COMPOSE) exec -it backend turtlemailctl initdata

.PHONY: test
test:
	$(COMPOSE) exec backend turtlemailctl test turtlemail

.PHONY: dump-fixtures
dump-fixtures:
	$(COMPOSE) exec backend turtlemailctl dumpdata --format yaml --natural-foreign --natural-primary --exclude auth --exclude contenttypes --exclude sessions > turtlemail/fixtures/initial_data.yaml
