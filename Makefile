PYTHON := $(if $(shell bash -c "command -v python3.10"), python3.10, python3)
PIP := $(if $(shell bash -c "command -v pip"), pip, pip3)
UV := $(uv)

cache:
	uv run -m scripts.synthea_cache_generator

kodjin-insert:
	HOST=http://localhost:4001/ uv run -m scripts.synthea_insert_resources

#port-forward to kauth service
locust:
	KODJIN_ROOT_DOMAIN=http://localhost:4003 MULTITENANCY_ENABLED=false uv run locust
