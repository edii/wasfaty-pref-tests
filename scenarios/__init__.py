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
            f"SELECT id, given, family, phone, gender, birth_date, address, city, state, tenant_id, owned_by "
            f"FROM patient WHERE id = {_id}"
        )
        row = res.fetchone()

        return {
            "id": row["id"],
            "given": row["given"],
            "family": row["family"],
            "phone": row["phone"],
            "gender": row["gender"],
            "birth_date": row["birth_date"],
            "address": row["address"],
            "city": row["city"],
            "state": row["state"],
            "multitenancy": {
                "tenant_id": row["tenant_id"],
                "owned_by": row["owned_by"],
            },
        }

    def get_random_observation_row(self):
        fixtures_manager = FixturesManager.get_instance()
        _id = random.randint(1, fixtures_manager.fixture("observations"))
        res = fixtures_manager.cursor().execute(
            f"SELECT id, issued, subject, status, code, encounter, category, value_quantity, value_concept, tenant_id, owned_by "
            f"FROM observation WHERE id = {_id}"
        )
        row = res.fetchone()

        return {
            "id": row["id"],
            "issued": row["issued"],
            "subject": row["subject"],
            "status": row["status"],
            "code": row["code"],
            "encounter": row["encounter"],
            "category": row["category"],
            "value_quantity": row["value_quantity"],
            "value_codeable_concept": row["value_concept"],
            "multitenancy": {
                "tenant_id": row["tenant_id"],
                "owned_by": row["owned_by"],
            },
        }

    def get_random_organization_row(self):
        fixtures_manager = FixturesManager.get_instance()
        _id = random.randint(1, fixtures_manager.fixture("organization"))
        res = fixtures_manager.cursor().execute(
            f"SELECT id, name, active, type, tenant_id, owned_by from organization where id = {_id}"
        )
        row = res.fetchone()

        return {
            "id": row["id"],
            "name": row["name"],
            "active": row["active"],
            "type": json.load(row["type"]),
            "multitenancy": {
                "tenant_id": row["tenant_id"],
                "owned_by": row["owned_by"],
            },
        }

    def get_random_practitioner_row(self):
        fixtures_manager = FixturesManager.get_instance()
        _id = random.randint(1, fixtures_manager.fixture("practitioner"))
        res = fixtures_manager.cursor().execute(
            f"SELECT id, identifier, active, name, tenant_id, owned_by from practitioner where id = {_id}"
        )
        row = res.fetchone()

        return {
            "id": row["id"],
            "identifier": json.load(row["identifier"]),
            "active": row["active"],
            "name": row["name"],
            "multitenancy": {
                "tenant_id": row["tenant_id"],
                "owned_by": row["owned_by"],
            },
        }

    def get_random_encounter_row(self):
        fixtures_manager = FixturesManager.get_instance()
        _id = random.randint(1, fixtures_manager.fixture("encounter"))
        res = fixtures_manager.cursor().execute(
            f"SELECT id, status, subject, period_start, period_end, tenant_id, owned_by  from encounter where id = {_id}"
        )
        row = res.fetchone()

        return {
            "id": row["id"],
            "status": row["status"],
            "subject": row["subject"],
            "start": row["period_start"],
            "end": row["period_end"],
            "multitenancy": {
                "tenant_id": row["tenant_id"],
                "owned_by": row["owned_by"],
            },
        }

    def get_random_condition_row(self):
        fixtures_manager = FixturesManager.get_instance()
        _id = random.randint(1, fixtures_manager.fixture("condition"))
        res = fixtures_manager.cursor().execute(
            f"SELECT id, subject, encounter, recorder, asserter, tenant_id, tenant_id from condition where id = {_id}"
        )
        row = res.fetchone()

        return {
            "id": row["id"],
            "subject": row["subject"],
            "encounter": row["encounter"],
            "recorder": row["recorder"],
            "asserter": row["asserter"],
            "multitenancy": {
                "tenant_id": row["tenant_id"],
                "owned_by": row["owned_by"],
            },
        }

    def get_random_composition_row(self):
        fixtures_manager = FixturesManager.get_instance()
        _id = random.randint(1, fixtures_manager.fixture("composition"))
        res = fixtures_manager.cursor().execute(
            f"SELECT id, subject, status, encounter, author, section, tenant_id, owned_by from composition where id = {_id}"
        )
        row = res.fetchone()

        return {
            "id": row["id"],
            "subject": row["subject"],
            "status": row["status"],
            "encounter": row["encounter"],
            "author": json.load(row["author"]),
            "section": json.load(row["section"]),
            "multitenancy": {
                "tenant_id": row["tenant_id"],
                "owned_by": row["owned_by"],
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
