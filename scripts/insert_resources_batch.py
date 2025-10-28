import os
import requests
import json
from templates import render_template
from util.ndjson_reader import NdjsonReader
from typing import List, Dict, Any


SOURCE_PATH = os.getenv("SOURCE_PATH", "./source")
# must be upload bundle
RESOURCE_TYPES = os.getenv("RESOURCES", "Patient,Organization,Practitioner,Encounter_Condition,Observation,Composition")
HOST = os.getenv("HOST", None)
SHOW_GROUPS_LOGS_INSERT_RESOURCES = os.getenv("SHOW_GROUPS_LOGS_INSERT_RESOURCES", False)
BATCH = os.getenv("INSERT_BATCH", 50)


def create_insert():
    if None in [HOST]:
        print("HOST env variable must be set")
        return

    ndjson_reader = NdjsonReader()

    for resource_type in RESOURCE_TYPES.split(","):
        print(f"Start insert {resource_type}")
        filepath = get_filepath(resource_type)
        _batch: List[ Dict | List[Dict] ] = []
        i = 1
        for record in ndjson_reader.read_records(filepath):
            i = i + 1

            _batch.append(record)
            if i % BATCH == 0:
                send_bundle(resource_type=resource_type, record_data=_batch)
                _batch.clear()

            if i % 1000 == 0:
                print(f"Processing [{i}].")

        if len(_batch) > 0:
            send_bundle(resource_type=resource_type, record_data=_batch)
            _batch.clear()

        print(f"All process {i}.")
        print(f"Done {resource_type}")

def get_filepath(resource_type):
    return f"{SOURCE_PATH}/{resource_type}.ndjson"

def prepare_record_data(resource_type: str, records: List[ Dict | List[Dict] ]) -> Any | None:
    entries: List[Dict] = []

    for record in records:
        if type(record) == dict:
            entries.append(json.loads(render_template(
                "bundle.entry", directory="insert", params={"record": record, "resource_type": resource_type}
            )))
        else:
            for item in record:
                entries.append(json.loads(render_template(
                    "bundle.entry", directory="insert", params={"record": item, "resource_type": item["resourceType"]}
                )))

    return json.loads(
        render_template(
            "bundle", directory="insert", params={"records": entries, "resource_type": resource_type}
        )
    )

def send_bundle(resource_type: str, record_data: List[ Dict | List[Dict] ]):
    headers = {
        "prefer": "respond-sync",
        "x-consumer-id": "pref-test",
        "Content-Type": "application/json",
    }

    response = requests.post(
        url=f"{HOST}",
        headers=headers,
        json=prepare_record_data(resource_type=resource_type, records=record_data),
        verify=True,
    )

    if response.status_code == 202 or response.status_code == 200:
        if SHOW_GROUPS_LOGS_INSERT_RESOURCES:
            print(
                f"Send insert for {resource_type}."
            )
    else:
        print(
            f"Failed to send insert with status code: {response.status_code}, response: {response.content}"
        )

if __name__ == '__main__':
    create_insert()
