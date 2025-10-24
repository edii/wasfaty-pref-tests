import sqlite3
from locust import events
from locust.env import Environment
from locust.runners import (
    WorkerRunner,
)
from settings import HEADERS, SYNTHEA_DB

# Dont work with this import (?)
# from scenarios.cockroachdb import CockroachResource
from scenarios.synthea import (
    SyntheaResource,
)
from fixtures_manager import FixturesManager

__all__ = ["SyntheaResource"]

common_header = HEADERS.copy()


@events.init.add_listener
def on_locust_init(environment: Environment, **kwargs):
    if SYNTHEA_DB is not None:
        con = sqlite3.connect(SYNTHEA_DB)
        con.row_factory = sqlite3.Row
        cursor = con.cursor()
        count_patients = int(
            cursor.execute(
                "SELECT count FROM counts WHERE table_name = 'patient'"
            ).fetchone()[0]
        )
        count_observations = int(
            cursor.execute(
                "SELECT count FROM counts WHERE table_name = 'observation'"
            ).fetchone()[0]
        )

        count_organization = int(
            cursor.execute(
                "SELECT count FROM counts WHERE table_name = 'organization'"
            ).fetchone()[0]
        )

        count_practitioner = int(
            cursor.execute(
                "SELECT count FROM counts WHERE table_name = 'practitioner'"
            ).fetchone()[0]
        )

        count_encounter = int(
            cursor.execute(
                "SELECT count FROM counts WHERE table_name = 'encounter'"
            ).fetchone()[0]
        )

        count_condition = int(
            cursor.execute(
                "SELECT count FROM counts WHERE table_name = 'condition'"
            ).fetchone()[0]
        )

        count_composition = int(
            cursor.execute(
                "SELECT count FROM counts WHERE table_name = 'composition'"
            ).fetchone()[0]
        )

        fixtures_manager = FixturesManager.get_instance()
        fixtures_manager.set_fixture("patients", count_patients)
        fixtures_manager.set_fixture("observations", count_observations)
        fixtures_manager.set_fixture("organization", count_organization)
        fixtures_manager.set_fixture("practitioner", count_practitioner)
        fixtures_manager.set_fixture("encounter", count_encounter)
        fixtures_manager.set_fixture("condition", count_condition)
        fixtures_manager.set_fixture("composition", count_composition)
        fixtures_manager.set_cursor(cursor)
