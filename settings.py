import os

API_URL = os.getenv("KODJIN_ROOT_DOMAIN")
CONSUMER_ID = os.getenv("CONSUMER_ID", "perf-kogin-test")
CACHE_DB = os.getenv("SYNTHEA_DB", "cache.db")
SCOPE_CFG = os.getenv("SCOPE_CFG", "scope.json")
AUTO_CLEANUP = False
VERIFY_SSL = True
ENV = os.getenv("ENV", "KODJIN")
HEADERS = {"x-consumer-id": f"{CONSUMER_ID}", "content-type": "application/json"}
