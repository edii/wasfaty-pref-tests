import os
import requests
import json
from templates import render_template
from util.ndjson_reader import NdjsonReader
from typing import List, Dict


SOURCE_PATH = os.getenv("SOURCE_PATH", "./source")
# must be upload bundle
RESOURCE_TYPES = os.getenv("RESOURCES", "Patient,Organization,Practitioner,Encounter_Condition,Observation,Composition")
# RESOURCE_TYPES = os.getenv("RESOURCES", "Composition") # test Patient,
HOST = os.getenv("HOST", None)
MULTITENANCY_ENABLED = os.getenv("MULTITENANCY_ENABLED", "false").lower() == "true"
TENANT_ID = os.getenv("TENANT_ID", "t4")
OWNED_BY = os.getenv("OWNED_BY", "o4")
ALL_TENANT_IDS = os.getenv("ALL_TENANT_IDS", "t1,t2,t3,t4,t5,t6,t7,t8")
ALL_OWNED_BY = os.getenv("ALL_OWNED_BY", "o1,o2,o3,o4,o5,o6,o7,o8")
SHOW_GROUPS_LOGS_INSERT_RESOURCES = os.getenv("SHOW_GROUPS_LOGS_INSERT_RESOURCES", True)


def create_insert():
    if None in [HOST]:
        print("HOST env variable must be set")
        return

    ndjson_reader = NdjsonReader()

    for resource_type in RESOURCE_TYPES.split(","):
        print(f"Start insert {resource_type}")
        filepath = get_filepath(resource_type)
        i = 1
        for record in ndjson_reader.read_records(filepath):
            i = i + 1
            create_bundle(resource_type=resource_type, record=record)

            if i % 1000 == 0:
                print(f"Processing [{i}].")

        print(f"All process {i}.")
        print(f"Done {resource_type}")

def get_filepath(resource_type):
    if MULTITENANCY_ENABLED:
        return f"{SOURCE_PATH}/{TENANT_ID}/{OWNED_BY}/{resource_type}.ndjson"

    return f"{SOURCE_PATH}/{resource_type}.ndjson"


def create_bundle(resource_type: str, record: List[Dict] | Dict):
    entry: List[Dict] = []
    if type(record) == dict:
        entry.append(json.loads(render_template(
            "entity", directory="insert", params={"record": record, "resource_type": resource_type}
        )))
    else:
        for item in record:
            entry.append(json.loads(render_template(
                "entity", directory="insert", params={"record": item, "resource_type": item["resourceType"]}
            )))

    request_data = json.loads(
        render_template(
            "insert", directory="insert", params={"record": entry, "resource_type": resource_type}
        )
    )

    headers = {
        "prefer": "respond-sync",
        "x-consumer-id": "pref-test",
        "Content-Type": "application/json",
    }

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
        verify=True,
    )

    if response.status_code == 202 or response.status_code == 200:
        if SHOW_GROUPS_LOGS_INSERT_RESOURCES is False:
            print(
                f"Send insert for {resource_type}."
            )
    else:
        print(
            f"Failed to send insert with status code: {response.status_code}, response: {response.content}"
        )


create_insert()
