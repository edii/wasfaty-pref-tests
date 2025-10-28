import os
import json
from templates import render_template
from util.ndjson_reader import NdjsonReader
from typing import List, Dict, Any
import asyncio
import aiohttp


SOURCE_PATH = os.getenv("SOURCE_PATH", "./source")
# must be upload bundle
RESOURCE_TYPES = os.getenv("RESOURCES", "Patient,Organization,Practitioner,Encounter_Condition,Observation,Composition")
HOST = os.getenv("HOST", None)
SHOW_GROUPS_LOGS_INSERT_RESOURCES = os.getenv("SHOW_GROUPS_LOGS_INSERT_RESOURCES", True)
BATCH = os.getenv("INSERT_BATCH", 50)
WORKER = os.getenv("NUMBER_WORKER", 5)


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

async def send_bundle(session, resource_type: str, record_data: List[ Dict | List[Dict] ]):
    try:
        headers = {
            "prefer": "respond-sync",
            "x-consumer-id": "pref-test",
            "Content-Type": "application/json",
        }

        async with session.post(url=f"{HOST}",
                                headers=headers,
                                json=prepare_record_data(resource_type=resource_type, records=record_data),
                                ssl=False) as response:
            response.raise_for_status()
            text = await response.text()

            return resource_type, response.status, text[:100]
    except aiohttp.ClientError as e:
        return resource_type, 500, str(e)


def params_batch(resource_type: str, ndjson_reader: NdjsonReader):
    filepath = get_filepath(resource_type)
    _batch: List[ Dict | List[Dict] ] = []
    _parts: List[ List[ Dict | List[Dict] ] ] = []
    print(f"filepath: {filepath}")
    i = 1
    for record in ndjson_reader.read_records(filepath):
        i = i + 1
        _batch.append(record)
        if i % BATCH == 0:
            _parts.append(_batch)
            _batch.clear()

        if len(_parts) == WORKER:
            send_data(resource_type, _parts)
            _parts.clear()

    if len(_batch) > 0:
        _parts.append(_batch)
        _batch.clear()

    if len(_parts) > 0:
        send_data(resource_type, _parts)
        _parts.clear()

    print(f"len__params: {len(_parts)}")

    # return _params

async def send_data(resource_type, parts):
    loop = asyncio.get_event_loop()
    conn = aiohttp.TCPConnector(limit=WORKER)
    session = aiohttp.ClientSession(connector=conn, loop=loop)
    async with session:
        tasks = [send_bundle(session=session, resource_type=resource_type, record_data=part) for part in parts]
        results = await asyncio.gather(*tasks)

        for res_type, status, content in results:
            if status < 200 or status > 299:
                raise Exception(f"ResourceType: {res_type}, Status: {status} Err: {content}")

            if SHOW_GROUPS_LOGS_INSERT_RESOURCES:
                print(f"ResourceType: {res_type}, Status: {status}")

async def main():
    if None in [HOST]:
        print("HOST env variable must be set")
        return

    ndjson_reader = NdjsonReader()

    for resource_type in RESOURCE_TYPES.split(","):
        filepath = get_filepath(resource_type)
        _batch: List[ Dict | List[Dict] ] = []
        _parts: List[ Any ] = []

        i = 1
        for record in ndjson_reader.read_records(filepath):
            i = i + 1
            _batch.append(record)
            if i % BATCH == 0:
                _parts.append(list(_batch))
                _batch.clear()


            if i % (WORKER * BATCH) == 0:
                await send_data(resource_type=resource_type, parts=_parts)
                _parts.clear()

            if i % 1000 == 0:
               print(f"Processing [{i}].")

        if len(_batch) > 0:
            _parts.append(list(_batch))
            _batch.clear()

        if len(_parts) > 0:
            await send_data(resource_type=resource_type, parts=_parts)
            _parts.clear()

        print(f"All process {i}.")
        print(f"Done {resource_type}")

if __name__ == "__main__":
    asyncio.run(main())
