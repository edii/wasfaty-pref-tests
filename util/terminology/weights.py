import random
import csv
from typing import Optional
from os import path


class Weights:
    def __init__(self, weights_dir: str, file: Optional[str] = None, data: list = []):
        self.codes = []
        self.weights = []

        if file is not None:
            weights_path = f"{weights_dir}/{file}.csv"

            if path.exists(weights_path):
                with open(weights_path) as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        self.append_item(row["CODE"], int(row["COUNT"]))
        elif data is not None:
            for item in data:
                self.append_item(item["CODE"], int(item["COUNT"]))

    def append_item(self, code: str, count: int):
        self.codes.append(code)
        self.weights.append(count)

    def pick(self) -> str:
        return random.choices(self.codes, self.weights)[0]
