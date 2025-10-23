PYTHON := $(if $(shell bash -c "command -v python3.10"), python3.10, python3)
PIP := $(if $(shell bash -c "command -v pip"), pip, pip3)
UV := $(uv)

cache:
	uv run -m scripts.synthea_cache_generator

kodjin-insert:
	HOST=https://webhook.site/75d35a10-9177-4fd6-aefe-4ef31db9a2e0 uv run -m scripts.synthea_insert_resources

locust:
	uv run locust
