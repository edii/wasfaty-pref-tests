import json
import logging
from typing import List, Optional, Dict


class Union:
    def __init__(self, name: str, resources: Optional[List] = None,
                 output_dir: str = "",
                 log: logging.Logger = None):
        self._name = name
        self._resources = resources
        self._total = 0
        self._output_dir = output_dir
        self._log = logging.getLogger(name)
        if log is not None:
            self._log = log

    def get_output_dir(self) -> str:
        return f"{self._output_dir}/{self._name}.ndjson"

    def get_resource_name(self, obj) -> str:
        return f"{type(obj).__name__}"

    def process(self, total: int = 0):
        self._log.info(f"Prepare {self._name}")

        if self._resources is None:
            raise Exception("resources not be empty")

        self._total = total
        for resource in self._resources:
            resource.process(total)

    def render_data(self, resource, params: List[Dict], current_index: int) -> Dict:
        try:
            new_param = params[current_index] | resource.union_refs(union_id=str(current_index+1))

            return json.loads(resource.render_data(new_param))
        except IndexError:

            return {}

    def create(self):
        self._log.info(f"Generating %s {self._name}", self._total)

        with open(self.get_output_dir(), "w") as output:
            for i in range(0, self._total):
                union_dict: List[Dict] = []

                for resource in self._resources:
                    union_dict.append(self.render_data(resource=resource, params=resource.get_params(), current_index=i))

                output.write(json.dumps(union_dict))
                output.write("\n")
