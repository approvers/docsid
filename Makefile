# CI
ifeq ($(DOCSID_IS_CI),"1")
    ifneq (,$(wildcard ./.env.ci))
        include .env.ci
        export
    else
        $(error ".env.ci file is missing")
    endif

# TEST
else ifeq ($(DOCSID_IS_TEST),"1")
    ifneq (,$(wildcard ./.env.test))
        include .env.test
        export
    else
        $(error ".env.test file is missing")
    endif

# LOCAL
else
    ifneq (,$(wildcard ./.env.example))
        include .env.example
        export
    else
        $(error ".env.example file is missing")
    endif

    ifneq (,$(wildcard ./.env.local))
        include .env.local
        export
    endif
endif

.PHONE: build
build:
	docker compose build --build-arg BUILDKIT_INLINE_CACHE=1

.PHONY: up
up:
	docker compose up -d --build
	$(MAKE) logs

.PHONY: down
down:
	docker compose down

.PHONY: restart
restart:
	docker compose restart

.PHONY: destroy
destroy:
	docker compose down --rmi all --volumes --remove-orphans

.PHONY: logs
logs:
	docker compose logs -f

.PHONY: shell
shell:
	docker compose run --rm api bash

.PHONY: flake8
flake8:
	docker compose run --rm api bash -c "python entry.py flake8 ./"

.PHONY: mypy
mypy:
	docker compose run --rm api bash -c "python entry.py mypy ./"

.PHONY: black
black:
	docker compose run --rm api bash -c "python entry.py black ./"

.PHONY: black_check
black_check:
	docker compose run --rm api bash -c "python entry.py black ./ --check"

.PHONY: pytest_html
pytest_html_report:
	docker compose run --rm api bash -c "pytest -v tests/ --cov=./src/ --html=report.html"

.PHONY: pytest_xml
pytest_xml:
	docker compose run --rm api bash -c "pytest -v tests/ --cov=./src/ --cov-report=xml"
