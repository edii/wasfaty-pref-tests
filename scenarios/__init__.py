import json

from locust import HttpUser, events, between
from fixtures_manager import FixturesManager
from settings import HEADERS
import time
import sys
import random


common_header = HEADERS.copy()


class FhirUser(HttpUser):
    wait_time = between(0, 0)

    def get_random_patient_row(self):
        fixtures_manager = FixturesManager.get_instance()
        _id = random.randint(1, fixtures_manager.fixture("patients"))
        res = fixtures_manager.cursor().execute(
            f"SELECT * from patient where id = {_id}"
        )
        row = res.fetchone()

        return {
            "id": row[1],
            "given": row[2],
            "family": row[3],
            "phone": row[4],
            "gender": row[5],
            "birth_date": row[6],
            "address": row[7],
            "city": row[8],
            "state": row[9],
            "multitenancy": {
                "tenant_id": row[10],
                "owned_by": row[11],
            },
        }

    def get_random_observation_row(self):
        fixtures_manager = FixturesManager.get_instance()
        _id = random.randint(1, fixtures_manager.fixture("observations"))
        res = fixtures_manager.cursor().execute(
            f"SELECT * from observation where id = {_id}"
        )
        row = res.fetchone()

        return {
            "id": row[1],
            "issued": row[2],
            "subject": row[3],
            "status": row[4],
            "code": row[5],
            "encounter": row[6],
            "category": row[7],
            "value_quantity": row[8],
            "value_codeable_concept": row[9],
            "multitenancy": {
                "tenant_id": row[10],
                "owned_by": row[11],
            },
        }

    def get_random_organization_row(self):
        fixtures_manager = FixturesManager.get_instance()
        _id = random.randint(1, fixtures_manager.fixture("organization"))
        res = fixtures_manager.cursor().execute(
            f"SELECT * from organization where id = {_id}"
        )
        row = res.fetchone()

        return {
            "id": row[1],
            "name": row[2],
            "active": row[3],
            "type": json.load(row[4]),
            "multitenancy": {
                "tenant_id": row[5],
                "owned_by": row[6],
            },
        }

    def get_random_practitioner_row(self):
        fixtures_manager = FixturesManager.get_instance()
        _id = random.randint(1, fixtures_manager.fixture("practitioner"))
        res = fixtures_manager.cursor().execute(
            f"SELECT * from practitioner where id = {_id}"
        )
        row = res.fetchone()

        return {
            "id": row[1],
            "identifier": json.load(row[2]),
            "active": row[3],
            "name": row[4],
            "multitenancy": {
                "tenant_id": row[5],
                "owned_by": row[6],
            },
        }

    def get_random_encounter_row(self):
        fixtures_manager = FixturesManager.get_instance()
        _id = random.randint(1, fixtures_manager.fixture("encounter"))
        res = fixtures_manager.cursor().execute(
            f"SELECT * from encounter where id = {_id}"
        )
        row = res.fetchone()

        return {
            "id": row[1],
            "status": row[2],
            "subject": row[3],
            "start": row[4],
            "end": row[5],
            "multitenancy": {
                "tenant_id": row[6],
                "owned_by": row[7],
            },
        }

    def get_random_condition_row(self):
        fixtures_manager = FixturesManager.get_instance()
        _id = random.randint(1, fixtures_manager.fixture("condition"))
        res = fixtures_manager.cursor().execute(
            f"SELECT * from condition where id = {_id}"
        )
        row = res.fetchone()

        return {
            "id": row[1],
            "subject": row[2],
            "encounter": row[3],
            "recorder": row[4],
            "asserter": row[5],
            "multitenancy": {
                "tenant_id": row[6],
                "owned_by": row[7],
            },
        }

    def get_random_composition_row(self):
        fixtures_manager = FixturesManager.get_instance()
        _id = random.randint(1, fixtures_manager.fixture("composition"))
        res = fixtures_manager.cursor().execute(
            f"SELECT * from composition where id = {_id}"
        )
        row = res.fetchone()

        return {
            "id": row[1],
            "subject": row[2],
            "status": row[3],
            "encounter": row[4],
            "author": json.load(row[5]),
            "section": json.load(row[6]),
            "multitenancy": {
                "tenant_id": row[7],
                "owned_by": row[8],
            },
        }

    def raise_failure(self, name, start, response):
        total = int((time.time() - start) * 1000)
        events.request_failure.fire(
            request_type="failure",
            name=name,
            response_time=total,
            response_length=sys.getsizeof(response),
            exception=response,
        )

    def raise_success(self, name, start, response):
        total = int((time.time() - start) * 1000)
        events.request_success.fire(
            request_type="success",
            name=name,
            response_time=total,
            response_length=sys.getsizeof(response),
            exception=response,
        )
