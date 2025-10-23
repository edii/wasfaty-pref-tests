import os
import requests
import json
from s3 import S3
from templates import render_template
from util.ndjson_reader import NdjsonReader
from typing import Dict


SOURCE_PATH = os.getenv("SOURCE_PATH", "./source")
RESOURCE_TYPES = os.getenv("RESOURCES", "Patient,Organization,Practitioner,Encounter,Condition,Observation,Composition")
HOST = os.getenv("HOST", None)
MULTITENANCY_ENABLED = os.getenv("MULTITENANCY_ENABLED", "false").lower() == "true"
TENANT_ID = os.getenv("TENANT_ID", "t4")
OWNED_BY = os.getenv("OWNED_BY", "o4")
ALL_TENANT_IDS = os.getenv("ALL_TENANT_IDS", "t1,t2,t3,t4,t5,t6,t7,t8")
ALL_OWNED_BY = os.getenv("ALL_OWNED_BY", "o1,o2,o3,o4,o5,o6,o7,o8")


def create_insert():
    if None in [HOST]:
        print("HOST env variable must be set")
        return

    ndjson_reader = NdjsonReader()

    for resource_type in RESOURCE_TYPES.split(","):
        filepath = get_filepath(resource_type)
        for record in ndjson_reader.read_records(filepath):
            create_bundle(resource_type=resource_type,record=record)


def get_filepath(resource_type):
    if MULTITENANCY_ENABLED:
        return f"{SOURCE_PATH}/{TENANT_ID}/{OWNED_BY}/{resource_type}.ndjson"

    return f"{SOURCE_PATH}/{resource_type}.ndjson"


def create_bundle(resource_type: str, record: Dict):
    request_data = json.loads(
        render_template(
            "insert", directory="insert", params={"record": record, "resource_type": resource_type}
        )
    )

    headers = {"prefer": "respond-async"}

    if MULTITENANCY_ENABLED:
        if resource_type == "Organization":
            headers["x-kodjin-metadata-tenant-id"] = ALL_TENANT_IDS
            headers["x-kodjin-metadata-owned-by"] = ALL_OWNED_BY
        else:
            headers["x-kodjin-metadata-tenant-id"] = TENANT_ID
            headers["x-kodjin-metadata-owned-by"] = OWNED_BY

    response = requests.post(
        url=f"{HOST}",
        headers=headers,
        json=request_data,
    )

    if response.status_code == 202:
        print(
            f"Send insert for {resource_type}: {response.headers['Content-Location']}"
        )
    else:
        print(
            f"Failed to send insert with status code: {response.status_code}, response: {response.content}"
        )


create_insert()
