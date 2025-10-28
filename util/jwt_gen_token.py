import json
from typing import Dict
import jwt
from datetime import datetime, timedelta, timezone

SECRET_KEY = "wasfaty-perf-test"
ALGORITHM = "HS256"


class JWTToken:
    def __init__(self, scope_path: str):
        self._scope: Dict = self.load_scope(scope_path)

    @staticmethod
    def load_scope(scope_path: str) -> Dict:
        data: Dict = {}

        with open(scope_path, "r") as file:
            data = json.load(file)

        return data

    def get_token(self) -> str:
        _scope = ""
        if "scope" in self._scope:
            _scope = self._scope["scope"]

        payload = {
            "scope": _scope,
            "exp": datetime.now(timezone.utc) + timedelta(minutes=12*60)
        }

        return jwt.encode(payload=payload, key=SECRET_KEY, algorithm=ALGORITHM)
