import logging
import json
from jinja2 import Environment
from faker import Faker
from util.consts import Status
from datetime import datetime
from typing import Dict, List
from util.helper.helper import random_list, random_birth_date
from util.consts import Gender


class Practitioner:
    TEMPLATE_NAME = "practitioner.json.jinja"

    def __init__(self, names: Dict, ages: Dict,
                 output_dir: str = "",
                 log: logging.Logger = logging.getLogger("practitioner"),
                 jinja: Environment = Environment,
                 faker: Faker = Faker):
        self._names = names
        self._ages = ages
        self._log = log
        self._jinja = jinja
        self._faker = faker
        self._output_dir = output_dir
        self._params: List[Dict] = []

    def get_output_dir(self) -> str:
        return f"{self._output_dir}/{type(self).__name__}.ndjson"

    def process(self, total: int = 0):
        self._log.info(f"Prepare practitioner")

        for i in range(0, total):
            _id = str(i+1)
            gender = random_list(Gender().get_all())
            first_name = random_list(self._names[gender]["first"])
            last_name = random_list(self._names[gender]["last"])
            (birth_date, age) = random_birth_date(self._ages, gender)
            mobile_number = self._faker.random_number(digits=10, fix_len=True)
            identifier = f"1{self._faker.random_number(digits=9, fix_len=True)}"

            param = {
                "id": _id,
                "gender": gender,
                "status": Status.GENERATED,
                "last_updated": datetime.now(),
                "identifier": identifier,
                "first_name": str(first_name["display"]),
                "first_name_en": first_name["code"],
                "last_name": last_name["display"],
                "last_name_en": last_name["code"],
                "telecom_email": self._faker.free_email(),
                "telecom_mobile": f'+30{mobile_number}',
                "birth_date": str(birth_date),
            }

            self._params.append(param)


    def get_params(self) -> List[Dict]:
        return self._params

    def create(self):
        self._log.info(f"Generating %s practitioner", len(self.get_params()))

        with open(self.get_output_dir(), "w") as output:
            for param in self.get_params():
                template = self._jinja.get_template(self.TEMPLATE_NAME)
                practitioner_data = template.render(param)

                output.write(json.dumps(json.loads(practitioner_data)))
                output.write("\n")

