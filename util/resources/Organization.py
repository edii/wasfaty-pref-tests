import logging
import json
from jinja2 import Environment
from faker import Faker
from util.consts import Status
from datetime import datetime
from typing import List, Dict
from util.helper.helper import random_randrange


class Organization:
    TEMPLATE_NAME = "organization.json.jinja"

    def __init__(self, output_dir: str = "", log: logging.Logger = logging.getLogger("organization"),
                 jinja: Environment = Environment,
                 faker: Faker = Faker):
        self._log = log
        self._jinja = jinja
        self._faker = faker
        self._output_dir = output_dir
        self._params: List[Dict] = []

    def get_output_dir(self) -> str:
        return f"{self._output_dir}/{type(self).__name__}.ndjson"

    def process(self, total: int = 0):
        self._log.info(f"Prepare organization")

        identifier = f"1{self._faker.random_number(digits=9, fix_len=True)}"
        mobile_number = self._faker.random_number(digits=10, fix_len=True)
        name = self._faker.company_suffix()

        for i in range(0, total):
            _id = str(i+1)

            param = {
                "id": _id,
                "name": f"test {name}",
                "status": Status.GENERATED,
                "last_updated": datetime.now(),
                "identifier": identifier,
                "telecom_mobile": f'+30{mobile_number}',
            }

            self._params.append(param)

    def get_params(self) -> List[Dict]:
        return self._params

    def create(self):
        self._log.info(f"Generating %s organization", len(self.get_params()))

        with open(self.get_output_dir(), "w") as output:
            for param in self.get_params():
                template = self._jinja.get_template(self.TEMPLATE_NAME)
                organization_data = template.render(param)

                output.write(json.dumps(json.loads(organization_data)))
                output.write("\n")
