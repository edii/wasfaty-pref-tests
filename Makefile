PYTHON := $(if $(shell bash -c "command -v python3.10"), python3.10, python3)
PIP := $(if $(shell bash -c "command -v pip"), pip, pip3)
UV := $(uv)

cache:
	uv run -m scripts.cache_generator

kodjin-insert-batch-async:
	HOST=http://localhost:4001/ uv run -m scripts.insert_resources_batch_async

kodjin-insert-batch:
	HOST=http://localhost:4001/ uv run -m scripts.insert_resources_batch

#port-forward to kauth service
locust:
	KODJIN_ROOT_DOMAIN=http://localhost:4003 uv run locust

data-gen:
	uv run -m scripts.data_generate
