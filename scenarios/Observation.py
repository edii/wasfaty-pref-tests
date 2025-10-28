from locust import task, tag
from . import FhirUser
from settings import HEADERS, VERIFY_SSL, SCOPE_CFG
from util.jwt_gen_token import JWTToken


class FhirClient(FhirUser):
    @staticmethod
    def get_token():
        j = JWTToken(scope_path=SCOPE_CFG)

        return j.get_token()

    def search_resource(self, resource_type, search_params, token: str = ""):
        headers = HEADERS.copy()
        headers["prefer"] = "handling=strict"
        params = search_params.split("&")
        name = []
        for param in params:
            name.append(param.split("=")[0])

        if token != "":
            headers["Authorization"] = f"bearer {token}"

        name = "_".join(name)
        with self.client.get(
            url=f"/search/{resource_type}?{search_params}",
            headers=headers,
            verify=VERIFY_SSL,
            name=name,
            catch_response=True,
        ) as response:
            response_json = self.try_return_json(response)

            if response.status_code != 200:
                response.failure(
                    f"Failed to search {resource_type}. Status code: {response.status_code}, response = {response_json}",
                )

            if not response_json.get("entry") or response_json is None:
                response.failure(
                    f"Bundle doesn't present in search, response = {response.text}"
                )

    def try_return_json(self, response):
        try:
            response_json = response.json()
        except Exception:
            return None
        return response_json


class ObservationResource(FhirClient):
    @task
    @tag("search", "search_observation_include_revinclude")
    def search_observation_include_revinclude(self):
        row = self.get_random_observation_row()
        self.search_resource(
            resource_type="Observation",
            search_params=f"_id={row['id']}&_include=Observation:performer:Practitioner&_revinclude=Composition:entry:Observation",
            token=self.get_token())


class CustomException(Exception):
    def __init__(self, message, status_code=None):
        super().__init__(message)
        self.status_code = status_code
