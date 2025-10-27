from locust import task, tag
from . import FhirUser
from settings import HEADERS, VERIFY_SSL, MULTITENANCY_ENABLED, SCOPE_CFG
from templates import render_template
import json
from util.jwt_gen_token import JWTToken


class SyntheaUser(FhirUser):
    @staticmethod
    def get_token():
        j = JWTToken(scope_path=SCOPE_CFG)

        return j.get_token()

    def multitenancy_headers(self, multitenancy):
        headers = HEADERS.copy()
        if MULTITENANCY_ENABLED:
            headers["x-kodjin-metadata-tenant-id"] = multitenancy["tenant_id"]
            headers["x-kodjin-metadata-owned-by"] = multitenancy["owned_by"]
        return headers

    def search_resource(self, resource_type, search_params, multitenancy, token: str = ""):
        headers = self.multitenancy_headers(multitenancy)
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

    def update_resource(self, resource_type, id, data, multitenancy, token: str = ""):
        headers = self.multitenancy_headers(multitenancy)

        if token != "":
            headers["Authorization"] = f"bearer {token}"

        with self.client.put(
            url=f"/api/{resource_type}/{id}",
            headers=headers,
            verify=VERIFY_SSL,
            name=f"Update {resource_type} by id",
            json=data,
            catch_response=True,
        ) as response:
            response_json = self.try_return_json(response)

            if response.status_code != 200:
                response.failure(
                    f"Failed to update {resource_type}. Status code: {response.status_code}, response = {response_json}",
                )
            # else:
            #     print(f"Updated {resource_type} with id: {id} ")

    def delete_resource(self, resource_type, id, multitenancy, token: str = ""):
        headers = self.multitenancy_headers(multitenancy)

        if token != "":
            headers["Authorization"] = f"bearer {token}"

        with self.client.delete(
            url=f"/api/{resource_type}/{id}",
            headers=headers,
            verify=VERIFY_SSL,
            name=f"Delete {resource_type} by id",
            catch_response=True,
        ) as response:
            response_json = self.try_return_json(response)

            if response.status_code != 204:
                response.failure(
                    f"Failed to delete {resource_type}. Status code: {response.status_code}, response = {response_json}",
                )
            # else:
            #     print(f"Deleted {resource_type} with id: {id} ")

    def create_resource(self, template_name, resource_type, params, token: str = ""):
        request_data = json.loads(
            render_template(template_name, directory="source", params=params)
        )

        headers = HEADERS

        if token != "":
            headers["Authorization"] = f"bearer {token}"

        with self.client.post(
            url=f"/api/{resource_type}",
            json=request_data,
            headers=headers,
            verify=VERIFY_SSL,
            name=f"Create {resource_type}",
            catch_response=True,
        ) as response:
            response_json = self.try_return_json(response)

        if response.status_code != 201:
            raise CustomException(
                f"{resource_type} failed to create. Status code: {response.status_code}, response = {response_json}",
                status_code=response.status_code,
            )

    def try_return_json(self, response):
        try:
            response_json = response.json()
        except Exception:
            return None
        return response_json


class SyntheaResource(SyntheaUser):
    @task
    @tag("search", "search_observation_include_revinclude")
    def search_observation_include_revinclude(self):
        row = self.get_random_observation_row()
        self.search_resource(
            resource_type="Observation",
            search_params=f"_id={row['id']}&_include=Observation:performer:Practitioner&_revinclude=Composition:entry:Observation",
            multitenancy=row["multitenancy"], token=self.get_token())


class CustomException(Exception):
    def __init__(self, message, status_code=None):
        super().__init__(message)
        self.status_code = status_code
