import json
import random
from dataclasses import dataclass
from typing import Optional
from os import path
from collections import OrderedDict
from .weights import Weights


@dataclass
class Concept:
    code: str
    display: str
    system: Optional[str]


class Resource:
    def __init__(self, resource_dir: str, weights_dir: str, name: str):
        self.concepts = OrderedDict()
        self.weights = None

        with open(f"{resource_dir}/{name}") as f:
            data = f.read()
            resource = json.loads(data)

            if resource["resourceType"] == "CodeSystem":
                concepts = resource["concept"]
            elif resource["resourceType"] == "ValueSet":
                concepts = resource["expansion"]["contains"]

            for concept in concepts:
                self.concepts[concept["code"]] = Concept(
                    concept["code"], concept["display"], concept.get("system")
                )

        weights_path = f"{weights_dir}/{name.removesuffix('.json')}.csv"
        if path.exists(weights_path):
            self.weights = Weights(weights_dir=weights_dir, file=name.removesuffix(".json"))

        weights_count = 0
        if self.weights is not None:
            weights_count = len(self.weights.weights)
        print(
            f"Loaded terminology resource {resource['id']} with {len(self.concepts)} concepts and {weights_count} weights"
        )

    def pick(self) -> Concept:
        if self.weights:
            code = self.weights.pick()
            return self.concepts[code]
        else:
            keys = list(self.concepts.keys())
            code = random.choice(keys)
            return self.concepts[code]
