# Everything you need is four commands.
VENV := .venv
PY   := $(VENV)/bin/python

.PHONY: help setup build drift probe add check clean

help:
	@echo "make setup              create .venv and install dependencies"
	@echo "make build              regenerate README.md, skill and connector pages"
	@echo "make drift              check every pointer against upstream, update baselines"
	@echo "make probe              re-probe vendor orgs for officially published skills"
	@echo "make add URL=... STAGE=n [AUTHORITY=first-party] [SYSTEMS=a,b]"
	@echo "make check              verify generated docs are in sync (what CI runs)"

$(PY):
	python3 -m venv $(VENV)
	$(VENV)/bin/pip install --quiet --upgrade pip
	$(VENV)/bin/pip install --quiet -r requirements.txt

setup: $(PY)
	@echo "ready — run 'make build'"

build: $(PY)
	@$(PY) scripts/build.py

# GITHUB_TOKEN lifts the 60-request anonymous rate limit; gh supplies one if present.
drift: $(PY)
	@GITHUB_TOKEN=$${GITHUB_TOKEN:-$$(gh auth token 2>/dev/null)} $(PY) scripts/check_drift.py --write
	@$(PY) scripts/build.py

probe: $(PY)
	@GITHUB_TOKEN=$${GITHUB_TOKEN:-$$(gh auth token 2>/dev/null)} $(PY) scripts/probe_skills.py --write \
		|| test $$? -eq 1   # exit 1 just means "new candidates to review"
	@$(PY) scripts/build.py

add: $(PY)
	@test -n "$(URL)"   || (echo "URL= is required, e.g. make add URL=https://github.com/o/r/tree/main/skills/x STAGE=6"; exit 1)
	@test -n "$(STAGE)" || (echo "STAGE= is required (0-7)"; exit 1)
	@GITHUB_TOKEN=$${GITHUB_TOKEN:-$$(gh auth token 2>/dev/null)} $(PY) scripts/add.py "$(URL)" \
		--stage $(STAGE) \
		--authority $${AUTHORITY:-community} \
		--systems $${SYSTEMS:-any}

check: build
	@git diff --exit-code -- README.md skills/ connectors/ docs/CONNECTOR-TRACKER.md \
		&& echo "generated docs are in sync" \
		|| (echo "out of date — commit the rebuild"; exit 1)

clean:
	rm -rf $(VENV)
