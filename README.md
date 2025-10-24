# wasfaty-perf-tests

### Installation
1. Install [uv](https://docs.astral.sh/uv/getting-started/installation/)
2. Install python:
    `uv python install 3.13`
3. Activate it:
    `uv python pin 3.13`
4. Sync `uv` environment:
    `uv sync`
5. Configure your IDE to use `ruff` formatter (e.g. [Visual Studio extension](https://marketplace.visualstudio.com/items?itemName=charliermarsh.ruff))
6. Run tests:
    `uv run locust`

### Test plan for perfomance testing
Before run tests need to scale fhir-server-fixtures-worker, fhir-server-search-fixtures-worker, fhir-terminology-fixtures-worker to 0

### Prepare data for testing
1. Create cache 
    `uv run -m scripts.synthea_cache_generator`
1. Create import for required resource:
    `HOST=https://kodjin-ffs-31322.edenlab.dev uv run -m scripts.synthea_insert_resources` where HOST - is your cluster's host

   
### POST resources
Tags
    `patient`
    `organization`
    `practitioner`
    `encounter`
    `condition`
    `observation`
    `composition`

### Search
Run this tag `precondition_search`, to generate patients with different values (`precondition_sd` must also be run, to create 10 StructureDefinitons)
