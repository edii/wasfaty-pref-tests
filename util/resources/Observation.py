import logging
import json
from jinja2 import Environment
from faker import Faker
from util.consts import Status
from datetime import datetime
from typing import List, Dict, Optional
from util.resources.Refs import Refs


class Observation:
    TEMPLATE_NAME = "observation.json.jinja"

    def __init__(self, output_dir: str = "",
                 log: logging.Logger = logging.getLogger("observation"),
                 jinja: Environment = Environment,
                 faker: Faker = Faker):
        self._log = log
        self._jinja = jinja
        self._faker = faker
        self._output_dir = output_dir
        self._params: List[Dict] = []
        self._refs: Optional[Refs] = None

    def set_refs(self, refs: Optional[Refs]):
        self._refs= refs

    def get_output_dir(self) -> str:
        return f"{self._output_dir}/{type(self).__name__}.ndjson"

    def validate(self):
        if self._refs is None:
            raise Exception("Required set refs object")

        if self._refs.is_organization_zero():
            raise Exception("Required ref for organization")

        if self._refs.is_patient_zero():
            raise Exception("Required ref for patient")

        if self._refs.is_practitioner_zero():
            raise Exception("Required ref for practitioner")

        if self._refs.is_encounter_zero():
            raise Exception("Required ref for encounter")

    def process(self, total: int = 0):
        self.validate()

        self._log.info(f"Prepare observation")

        for i in range(0, total):
            _id = str(i+1)

            param = {
                "id": _id,
                "status_text": Status.GENERATED,
                "status": Status.FINAL,
                "last_updated": datetime.now(),
                "ref_organization": self._refs.get_ref_organization(),
                "ref_patient": self._refs.get_ref_patient(),
                "ref_practitioner": self._refs.get_ref_practitioner(),
                "ref_encounter": self._refs.get_ref_encounter(),
            }

            self._params.append(param)

    def get_params(self) -> List[Dict]:
        return self._params

    def create(self):
        self._log.info(f"Generating %s observation", len(self.get_params()))

        with open(self.get_output_dir(), "w") as output:
            for param in self.get_params():
                template = self._jinja.get_template(self.TEMPLATE_NAME)
                observation_data = template.render(param)

                output.write(json.dumps(json.loads(observation_data)))
                output.write("\n")
