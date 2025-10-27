import os

API_URL = os.getenv("KODJIN_ROOT_DOMAIN")
CONSUMER_ID = os.getenv("CONSUMER_ID", "perf-kogin-test")
SYNTHEA_DB = os.getenv("SYNTHEA_DB", "synthea.db")
SCOPE_CFG = os.getenv("SCOPE_CFG", "scope.json")

AUTO_CLEANUP = False
VERIFY_SSL = True

# HAPY, ZOADIGM, KODJIN
# TODO: figure out if it's needed (or use tags?)
ENV = os.getenv("ENV", "KODJIN")

HEADERS = {"x-consumer-id": f"{CONSUMER_ID}", "content-type": "application/json"}
MULTITENANCY_ENABLED = os.getenv("MULTITENANCY_ENABLED", "false").lower() == "true"
