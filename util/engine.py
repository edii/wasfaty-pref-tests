import logging
from jinja2 import Environment
from faker import Faker
from typing import Dict
from util.resources.Organization import Organization
from util.resources.Practitioner import Practitioner
from util.resources.Patient import Patient
from util.resources.Encounter import Encounter
from util.resources.Condition import Condition
from util.resources.Observation import Observation
from util.resources.Composition import Composition
from util.resources.Union import Union
from util.resources.Refs import Refs


class Engine:

    def __init__(self, cfg: Dict,
                 names: Dict,
                 ages: Dict,
                 terminology: Dict,
                 output_dir: str = "",
                 log: logging.Logger = logging.getLogger("engine"),
                 jinja: Environment = Environment,
                 faker: Faker = Faker):
        self._cfg = cfg
        self._output_dir = output_dir
        self._log = log
        self._refs = Refs(
            organization_total=cfg["organization_total"],
            patient_total=cfg["patient_total"],
            practitioner_total=cfg["practitioner_total"],
            encounter_total=cfg["encounter_condition"],
            observation_total=cfg["observation_total"],
            condition_total=cfg["encounter_condition"],
        )

        self._organization = Organization(output_dir=output_dir, log=log, jinja=jinja, faker=faker)
        self._practitioner = Practitioner(
            names=names, ages=ages, output_dir=output_dir, log=log, jinja=jinja, faker=faker)
        self._patient = Patient(
            names=names, ages=ages, terminology=terminology,output_dir=output_dir, log=log, jinja=jinja, faker=faker)
        self._encounter = Encounter(output_dir=output_dir, log=log, jinja=jinja, faker=faker)
        self._condition = Condition(output_dir=output_dir, log=log, jinja=jinja, faker=faker)
        self._observation = Observation(output_dir=output_dir, log=log, jinja=jinja, faker=faker)
        self._composition = Composition(output_dir=output_dir, log=log, jinja=jinja, faker=faker)

    def run(self):
        #Refs
        self._encounter.set_refs(self._refs)
        self._condition.set_refs(self._refs)
        self._observation.set_refs(self._refs)
        self._composition.set_refs(self._refs)

        # Organization
        self._organization.process(self._cfg["organization_total"])
        self._organization.create()

        # Practitioner
        self._practitioner.process(self._cfg["practitioner_total"])
        self._practitioner.create()

        # Patient
        self._patient.process(self._cfg["patient_total"])
        self._patient.create()

        # union Encounter_Condition
        union_encounter_condition = Union(
            name="Encounter_Condition",
            resources=[self._encounter, self._condition],
            output_dir=self._output_dir,
            log=self._log)
        union_encounter_condition.process(self._cfg["encounter_condition"])
        union_encounter_condition.create()

        # Observation
        self._observation.process(self._cfg["observation_total"])
        self._observation.create()

        # Composition
        self._composition.process(self._cfg["composition_total"])
        self._composition.create()
