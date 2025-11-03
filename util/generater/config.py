import yaml
import json
import csv
from pathlib import Path
from typing import Dict
from util.terminology.resource import Resource


class Config:
    @staticmethod
    def load_settings(cfg_path: str) -> Dict:
        with open(cfg_path) as f:
            cfg = yaml.safe_load(f)

        settings = {**cfg.get("settings", {})}

        return settings

    @staticmethod
    def load_names(names_path: str) -> Dict:
        with open(names_path) as f:
            data = f.read()

        names = json.loads(data)

        return names

    @staticmethod
    def load_ages(ages_path: str) -> Dict:
        ages = {}
        with open(ages_path) as f:
            reader = csv.DictReader(f)
            for row in reader:
                raw_age = row["Age"]
                if "+" in raw_age:
                    continue

                ages[int(raw_age)] = {
                    "male": int(row["M"]),
                    "female": int(row["F"]),
                }

        return ages

    @staticmethod
    def load_terminology(terminology_dir: str, weights_dir: str) -> Dict:
        terminology = {}
        for entry in Path(terminology_dir).iterdir():
            base_name = entry.name.removesuffix(".json")
            terminology[base_name] = Resource(
                resource_dir=terminology_dir, weights_dir=weights_dir, name=entry.name)

        return terminology
