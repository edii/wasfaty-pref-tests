import sqlite3
import os
import json
from s3 import S3
from progress.bar import ChargingBar
from util.ndjson_reader import NdjsonReader
from typing import Dict

# RESOURCES_TOTAL
PATIENT_TOTAL = os.getenv("PATIENT_TOTAL", 10)
ORGANIZATION_TOTAL = os.getenv("ORGANIZATION_TOTAL", 1)
PRACTITIONER_TOTAL = os.getenv("PRACTITIONER_TOTAL", 20)
# ENCOUNTER_TOTAL = os.getenv("ENCOUNTER_TOTAL", 100)
# CONDITION_TOTAL = os.getenv("CONDITION_TOTAL", 4)
ENCOUNTER_CONDITION_TOTAL = os.getenv("ENCOUNTER_CONDITION_TOTAL", 100)
OBSERVATION_TOTAL = os.getenv("OBSERVATION_TOTAL", 700800)
COMPOSITION_TOTAL = os.getenv("COMPOSITION_TOTAL", 233600)

SOURCE_PATH = os.getenv("SOURCE_PATH", "./source")
SQLITE_PATH = os.getenv("SQLITE_PATH", "./synthea.db")
MULTITENANCY_ENABLED = os.getenv("MULTITENANCY_ENABLED", "false").lower() == "true"
TENANT_ID = os.getenv("TENANT_ID", "")
OWNED_BY = os.getenv("OWNED_BY", "")
ALL_TENANT_IDS = os.getenv("ALL_TENANT_IDS", "t1,t2,t3,t4,t5,t6,t7,t8")
ALL_OWNED_BY = os.getenv("ALL_OWNED_BY", "o1,o2,o3,o4,o5,o6,o7,o8")
CHUNK_SIZE = 2048


class Counter:
    def __init__(self, resource_type, max):
        self.count = 0
        self.resource_type = resource_type
        self.bar = ChargingBar(f"Processing {resource_type} resources", max=max)

    def increment(self, bar_state):
        self.count += 1
        self.bar.goto(bar_state)

    def next(self):
        self.count += 1
        self.bar.next()

    def finish(self):
        self.bar.finish()
        print(f"Uploaded {self.count} of {self.resource_type} resources\n")


class Inserter:
    def __init__(self):
        self.con = sqlite3.connect(SQLITE_PATH)
        self.cursor = self.con.cursor()

    def cache_patients(self, ndjson_reader: NdjsonReader):
        self.cursor.execute(
            """CREATE TABLE IF NOT EXISTS patient(
                id INTEGER PRIMARY KEY,
                given TEXT,
                family TEXT,
                phone TEXT,
                gender TEXT,
                birth_date TEXT,
                address TEXT,
                city TEXT,
                state TEXT,
                tenant_id TEXT,
                owned_by TEXT
            )
            """
        )
        self.commit()

        self.cursor.execute("DELETE FROM patient")
        self.commit()

        resource_type = "Patient"
        filepath = get_filepath(resource_type)
        counter = Counter(resource_type=resource_type, max=int(PATIENT_TOTAL))
        for data in ndjson_reader.read_records(filepath):
            given = None
            family = None
            if len(data["name"]) > 0:
                name = data["name"][0]
                given = ",".join(name["given"])
                family = name["family"]

            phone = None
            if len(data["telecom"]) > 0:
                telecom = data["telecom"][0]
                if telecom["system"] == "phone":
                    phone = telecom["value"]

            city = None
            state = None
            if len(data["address"]) > 0:
                address = data["address"][0]
                city = address["city"]
                state = address["state"]

            self.cursor.execute(
                """INSERT INTO patient
                (id, given, family, phone, gender, birth_date, city, state, tenant_id, owned_by)
                VALUES
                (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    data["id"],
                    given,
                    family,
                    phone,
                    data["gender"],
                    data["birthDate"],
                    city,
                    state,
                    TENANT_ID,
                    OWNED_BY,
                ),
            )

            counter.next()

        self.commit()
        counter.finish()

    def cache_organizations(self, ndjson_reader: NdjsonReader):
        self.cursor.execute(
            """CREATE TABLE IF NOT EXISTS organization(
                id INTEGER PRIMARY KEY,
                name TEXT,
                active INTEGER,
                type TEXT,
                tenant_id TEXT,
                owned_by TEXT
            )
            """
        )
        self.commit()

        self.cursor.execute("DELETE FROM organization")
        self.commit()

        resource_type = "Organization"
        filepath = get_filepath(resource_type)
        counter = Counter(resource_type=resource_type, max=int(ORGANIZATION_TOTAL))
        for data in ndjson_reader.read_records(filepath):
            self.cursor.execute(
                """INSERT INTO organization
                (id, name, active, type, tenant_id, owned_by)
                VALUES
                (?, ?, ?, ?, ?, ?)
            """,
                (
                    data["id"],
                    data["name"],
                    data["active"],
                    json.dumps(data["type"]),
                    ALL_TENANT_IDS,
                    ALL_OWNED_BY,
                ),
            )
            counter.next()

        self.commit()
        counter.finish()

    def cache_practitioner(self, ndjson_reader: NdjsonReader):
        self.cursor.execute(
            """CREATE TABLE IF NOT EXISTS practitioner(
                id INTEGER PRIMARY KEY,
                identifier TEXT,
                active INTEGER,
                name TEXT,
                tenant_id TEXT,
                owned_by TEXT
            )
            """
        )
        self.commit()

        self.cursor.execute("DELETE FROM practitioner")
        self.commit()

        resource_type = "Practitioner"
        filepath = get_filepath(resource_type)
        counter = Counter(resource_type=resource_type, max=int(PRACTITIONER_TOTAL))
        for data in ndjson_reader.read_records(filepath):
            name = None
            if len(data["name"]) > 0:
                name = data["name"][0]["family"]

            self.cursor.execute(
                """INSERT INTO practitioner
                (id, identifier, active, name, tenant_id, owned_by)
                VALUES
                (?, ?, ?, ?, ?, ?)
            """,
                (
                    data["id"],
                    json.dumps(data["identifier"]),
                    data["active"],
                    name,
                    TENANT_ID,
                    OWNED_BY,
                ),
            )
            counter.next()

        self.commit()
        counter.finish()

    def cache_encounter_condition(self, ndjson_reader: NdjsonReader):
        self.cursor.execute(
            """CREATE TABLE IF NOT EXISTS encounter(
                                                       id INTEGER PRIMARY KEY,
                                                       status TEXT,
                                                       subject TEXT,
                                                       period_start TEXT,
                                                       period_end TEXT,
                                                       tenant_id TEXT,
                                                       owned_by TEXT
               )
            """
        )
        self.commit()

        self.cursor.execute("DELETE FROM encounter")
        self.commit()

        self.cursor.execute(
            """CREATE TABLE IF NOT EXISTS condition(
                                                       id INTEGER PRIMARY KEY,
                                                       subject TEXT,
                                                       encounter TEXT,
                                                       recorder TEXT,
                                                       asserter TEXT,
                                                       tenant_id TEXT,
                                                       owned_by TEXT
               )
            """
        )

        self.commit()

        self.cursor.execute("DELETE FROM condition")
        self.commit()

        resource_type = "Encounter_Condition"
        filepath = get_filepath(resource_type)
        counter = Counter(resource_type=resource_type, max=int(ENCOUNTER_CONDITION_TOTAL))
        for records in ndjson_reader.read_records(filepath):
            for data in records:
                if data["resourceType"] == "Encounter":
                    self.set_encounter(data)
                if data["resourceType"] == "Condition":
                    self.set_condition(data)

            counter.next()
            if counter.count % 100000 == 0:
                self.commit()

        self.commit()
        counter.finish()

    def set_encounter(self, data: Dict):
        start = ''
        if "start" in data["period"]:
            start = data["period"]["start"]

        end = ''
        if "end" in data["period"]:
            end = data["period"]["end"]

        self.cursor.execute(
            """INSERT INTO encounter
            (id, status, subject, period_start, period_end, tenant_id, owned_by)
            VALUES
            (?, ?, ?, ?, ?, ?, ?)
        """,
            (
                data["id"],
                data["status"],
                data["subject"]["reference"],
                start,
                end,
                TENANT_ID,
                OWNED_BY,
            ),
        )

    def set_condition(self, data: Dict):
        self.cursor.execute(
            """INSERT INTO condition
               (id, subject, encounter, recorder, asserter, tenant_id, owned_by)
               VALUES
                   (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                data["id"],
                data["subject"]["reference"],
                data["encounter"]["reference"],
                data["recorder"]["reference"],
                data["asserter"]["reference"],
                TENANT_ID,
                OWNED_BY,
            ),
        )

    def cache_composition(self, ndjson_reader: NdjsonReader):
        self.cursor.execute(
            """CREATE TABLE IF NOT EXISTS composition(
                   id INTEGER PRIMARY KEY,
                   subject TEXT,
                   status TEXT,
                   encounter TEXT,
                   author TEXT,
                   section TEXT, 
                   tenant_id TEXT,
                   owned_by TEXT
               )
            """
        )

        self.commit()

        self.cursor.execute("DELETE FROM composition")
        self.commit()

        resource_type = "Composition"
        filepath = get_filepath(resource_type)
        counter = Counter(resource_type=resource_type, max=int(COMPOSITION_TOTAL))
        for data in ndjson_reader.read_records(filepath):

            self.cursor.execute(
                """INSERT INTO composition
                       (id, subject, status, encounter, author, section, tenant_id, owned_by)
                   VALUES
                       (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    data["id"],
                    data["subject"]["reference"],
                    data["status"],
                    data["encounter"]["reference"],
                    json.dumps(data["author"]),
                    json.dumps(data["section"]),
                    TENANT_ID,
                    OWNED_BY,
                ),
            )
            counter.next()
            if counter.count % 100000 == 0:
                self.commit()

        self.commit()
        counter.finish()

    def cache_observation(self, ndjson_reader: NdjsonReader):
        self.cursor.execute(
            """CREATE TABLE IF NOT EXISTS observation(
                id INTEGER PRIMARY KEY,
                issued TEXT,
                subject TEXT,
                status TEXT,
                code TEXT,
                encounter TEXT,
                category TEXT,
                value_quantity TEXT,
                value_concept TEXT,
                tenant_id TEXT,
                owned_by TEXT
            )
            """
        )

        self.commit()

        self.cursor.execute("DELETE FROM observation")
        self.commit()

        resource_type = "Observation"
        filepath = get_filepath(resource_type)
        counter = Counter(resource_type=resource_type, max=int(OBSERVATION_TOTAL))
        for data in ndjson_reader.read_records(filepath):

            value_quantity = None
            value_concept = None

            # skip observations without valueQuantity
            if "valueQuantity" in data:
                value_quantity = json.dumps(data["valueQuantity"])
            elif "valueCodeableConcept" in data:
                value_concept = json.dumps(data["valueCodeableConcept"])
            else:
                continue

            issued = ""
            if "issued" in data:
                issued = data["issued"]

            self.cursor.execute(
                """INSERT INTO observation
                (id, issued, subject, status, code, encounter, category, value_quantity, value_concept, tenant_id, owned_by)
                VALUES
                (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    data["id"],
                    issued,
                    data["subject"]["reference"],
                    data["status"],
                    json.dumps(data["code"]),
                    data["encounter"]["reference"],
                    json.dumps(data["category"]),
                    value_quantity,
                    value_concept,
                    TENANT_ID,
                    OWNED_BY,
                ),
            )
            counter.next()
            if counter.count % 100000 == 0:
                self.commit()

        self.commit()
        counter.finish()

    def cache_counts(self):
        self.cursor.execute(
            """CREATE TABLE IF NOT EXISTS counts(
                table_name TEXT PRIMARY KEY,
                count INTEGER
            )
            """
        )

        self.commit()

        patient_count = int(
            self.cursor.execute("SELECT count(*) from patient").fetchone()[0]
        )
        print(f"Patient count: {patient_count}")

        observation_count = int(
            self.cursor.execute("SELECT count(*) from observation").fetchone()[0]
        )
        print(f"Observation count: {observation_count}")

        organization_count = int(
            self.cursor.execute("SELECT count(*) from organization").fetchone()[0]
        )
        print(f"Organization count: {organization_count}")

        practitioner_count = int(
            self.cursor.execute("SELECT count(*) from practitioner").fetchone()[0]
        )
        print(f"Practitioner count: {practitioner_count}")

        encounter_count = int(
            self.cursor.execute("SELECT count(*) from encounter").fetchone()[0]
        )
        print(f"Encounter count: {encounter_count}")

        condition_count = int(
            self.cursor.execute("SELECT count(*) from condition").fetchone()[0]
        )
        print(f"Condition count: {condition_count}")

        composition_count = int(
            self.cursor.execute("SELECT count(*) from composition").fetchone()[0]
        )
        print(f"Composition count: {composition_count}")

        self.cursor.execute("""DELETE from counts""")

        self.commit()

        self.cursor.executemany(
            """INSERT INTO counts
            (table_name, count)
            VALUES
            (?, ?)
        """,
            [
                ("patient", patient_count),
                ("observation", observation_count),
                ("organization", organization_count),
                ("practitioner", practitioner_count),
                ("encounter", encounter_count),
                ("condition", condition_count),
                ("composition", composition_count),
            ],
        )

        self.commit()

    def commit(self):
        self.con.commit()

def get_filepath(resource_type):
    if MULTITENANCY_ENABLED:
        return f"{SOURCE_PATH}/{TENANT_ID}/{OWNED_BY}/{resource_type}.ndjson"

    return f"{SOURCE_PATH}/{resource_type}.ndjson"


# Create synthea.db from s3 data
def prepare_db():
    inserter = Inserter()

    nr = NdjsonReader()

    inserter.cache_patients(nr)
    inserter.cache_organizations(nr)
    inserter.cache_practitioner(nr)

    # union
    inserter.cache_encounter_condition(nr)

    # inserter.cache_encounter(nr)
    inserter.cache_observation(nr)
    # inserter.cache_condition(nr)
    inserter.cache_composition(nr)

    inserter.cache_counts()


prepare_db()
