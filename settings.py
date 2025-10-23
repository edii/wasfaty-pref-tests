import os

API_URL = os.getenv("KODJIN_ROOT_DOMAIN")
CONSUMER_ID = os.getenv("CONSUMER_ID", "perf-kogin-test")
SYNTHEA_DB = os.getenv("SYNTHEA_DB", "synthea.db")
#
# COCKROACH_DB_URL = os.getenv(
#     "COCKROACH_DB_URL", "postgresql://root@localhost:26257/ehr_search?sslmode=disable"
# )

AUTO_CLEANUP = False
VERIFY_SSL = True

# HAPY, ZOADIGM, KODJIN
# TODO: figure out if it's needed (or use tags?)
ENV = os.getenv("ENV", "KODJIN")

HEADERS = {"x-consumer-id": f"{CONSUMER_ID}", "content-type": "application/json"}
MULTITENANCY_ENABLED = os.getenv("MULTITENANCY_ENABLED", "false").lower() == "true"
