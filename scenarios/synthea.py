from locust import task, tag
from . import FhirUser
from settings import HEADERS, VERIFY_SSL, MULTITENANCY_ENABLED
from templates import render_template
from datetime import datetime, timezone
from functools import wraps
import json
import time

class SyntheaUser(FhirUser):
    def multitenancy_headers(self, multitenancy):
        headers = HEADERS.copy()
        if MULTITENANCY_ENABLED:
            headers["x-kodjin-metadata-tenant-id"] = multitenancy["tenant_id"]
            headers["x-kodjin-metadata-owned-by"] = multitenancy["owned_by"]
        return headers

    def search_resource(self, resource_type, search_params, multitenancy):
        headers = self.multitenancy_headers(multitenancy)
        headers["prefer"] = "handling=strict"
        params = search_params.split("&")
        name = []
        for param in params:
            name.append(param.split("=")[0])

        name = "_".join(name)
        with self.client.get(
            url=f"/fhir/{resource_type}?{search_params}",
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

            if not response_json.get("entry"):
                response.failure(
                    f"Bundle doesn't present in search, response = {response.text}"
                )

    def update_resource(self, resource_type, id, data, multitenancy):
        headers = self.multitenancy_headers(multitenancy)
        with self.client.put(
            url=f"/fhir/{resource_type}/{id}",
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

    def delete_resource(self, resource_type, id, multitenancy):
        headers = self.multitenancy_headers(multitenancy)
        with self.client.delete(
            url=f"/fhir/{resource_type}/{id}",
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

    def create_resource(self, template_name, resource_type, params):
        request_data = json.loads(
            render_template(template_name, directory="source", params=params)
        )
        with self.client.post(
            url=f"/fhir/{resource_type}",
            json=request_data,
            headers=HEADERS,
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
    @tag("search", "search_patient_by_id")
    def search_patient_by_id(self):
        row = self.get_random_patient_row()
        self.search_resource("Patient", f"_id={row['id']}", row["multitenancy"])

    # @task
    # @tag("search", "search_patient_identifier")
    # def search_patient_identifier(self):
    #     row = self.get_random_patient_row()
    #     self.search_resource("Patient", f"identifier={row['id']}", row["multitenancy"])
    #
    # @task
    # @tag("search", "search_patient_of_type_identifier")
    # def search_patient_of_type_identifier(self):
    #     row = self.get_random_patient_row()
    #     self.search_resource(
    #         "Patient",
    #         f"identifier:of-type=http://terminology.hl7.org/CodeSystem/v2-0203|NI|{row['id']}",
    #         row["multitenancy"],
    #     )
    #
    # @task
    # @tag("search", "search_patient_family_given")
    # def search_patient_family_given(self):
    #     row = self.get_random_patient_row()
    #     given = row["given"].split(",")[0]
    #     self.search_resource(
    #         "Patient",
    #         f"family={row['family']}&given={given}&_count=1",
    #         row["multitenancy"],
    #     )
    #
    # @task
    # @tag("search", "search_patient_exact_family_given")
    # def search_patient_exact_family_given(self):
    #     row = self.get_random_patient_row()
    #     given = row["given"].split(",")[0]
    #     self.search_resource(
    #         "Patient",
    #         f"family:exact={row['family']}&given:exact={given}",
    #         row["multitenancy"],
    #     )
    #
    # @task
    # @tag("search", "search_patient_family_given_birth_date")
    # def search_patient_family_given_birth_date(self):
    #     row = self.get_random_patient_row()
    #     given = row["given"].split(",")[0]
    #     self.search_resource(
    #         "Patient",
    #         f"family={row['family']}&given={given}&birthdate={row['birth_date']}",
    #         row["multitenancy"],
    #     )
    #
    # @task
    # @tag("search", "search_patient_telecom")
    # def search_patient_telecom(self):
    #     row = self.get_random_patient_row()
    #     self.search_resource("Patient", f"telecom={row['phone']}", row["multitenancy"])
    #
    # @task
    # @tag("search", "search_patient_family_given_city_state")
    # def search_patient_family_given_city_state(self):
    #     row = self.get_random_patient_row()
    #     given = row["given"].split(",")[0]
    #     self.search_resource(
    #         "Patient",
    #         f"family={row['family']}&given={given}&address-city={row['city']}&address-state={row['state']}&_count=1",
    #         row["multitenancy"],
    #     )
    #
    # @task
    # @tag("search", "search_patient_city_state")
    # def search_patient_city_state(self):
    #     row = self.get_random_patient_row()
    #     self.search_resource(
    #         "Patient",
    #         f"address-city={row['city']}&address-state={row['state']}&_count=1",
    #         row["multitenancy"],
    #     )

    # @task
    # @tag("search", "search_observation_patient")
    # def search_observation_patient(self):
    #     row = self.get_random_observation_row()
    #     self.search_resource(
    #         "Observation", f"subject={row['subject']}&_count=1", row["multitenancy"]
    #     )
    #
    # @task
    # @tag("search", "search_observation_code")
    # def search_observation_code(self):
    #     row = self.get_random_observation_row()
    #     code = json.loads(row["code"])["coding"][0]["code"]
    #     self.search_resource("Observation", f"code={code}", row["multitenancy"])
    #
    # @task
    # @tag("search", "search_observation_system_code")
    # def search_observation_system_code(self):
    #     row = self.get_random_observation_row()
    #     code = json.loads(row["code"])["coding"][0]["code"]
    #     system = json.loads(row["code"])["coding"][0]["system"]
    #     self.search_resource(
    #         "Observation", f"code={system}|{code}", row["multitenancy"]
    #     )
    #
    # @task
    # @tag("search", "search_observation_text_code")
    # def search_observation_text_code(self):
    #     row = self.get_random_observation_row()
    #     text = json.loads(row["code"])["text"]
    #     self.search_resource("Observation", f"code:text={text}", row["multitenancy"])
    #
    # @task
    # @tag("search", "search_observation_code_value_quantity")
    # def search_observation_code_value_quantity(self):
    #     row = self.get_random_observation_row()
    #     code = json.loads(row["code"])["coding"][0]["code"]
    #     value_quantity = json.loads(row["value_quantity"])["value"]
    #     self.search_resource(
    #         "Observation",
    #         f"code={code}&value-quantity=gt{value_quantity}",
    #         row["multitenancy"],
    #     )
    #
    # @task
    # @tag("search", "search_observation_value_quantity_value_code_code")
    # def search_observation_value_quantity_value_code_code(self):
    #     row = self.get_random_observation_row()
    #     code = json.loads(row["code"])["coding"][0]["code"]
    #     self.search_resource(
    #         "Observation",
    #         f"code={code}&value-quantity={row['value']}||{row['unit']}",
    #         row["multitenancy"],
    #     )
    #
    # @task
    # @tag("search", "search_observation_value_quantity_value_system_code_code")
    # def search_observation_value_quantity_value_system_code_code(self):
    #     row = self.get_random_observation_row()
    #     code = json.loads(row["code"])["coding"][0]["code"]
    #     self.search_resource(
    #         "Observation",
    #         f"code={code}&value-quantity={row['value']}|http://unitsofmeasure.org|{row['unit']}",
    #         row["multitenancy"],
    #     )
    #
    # @task
    # @tag("search", "delete_observation_by_id")
    # def delete_observation_by_id(self):
    #     row = self.get_random_observation_row()
    #     self.delete_resource("Observation", row["id"], row["multitenancy"])

    # @task
    # @tag("search", "update_observation_by_id")
    # def update_observation_by_id(self):
    #     row = self.get_random_observation_row()
    #     row["description"] = f"{row['description']} {int(time.time())}"
    #     request_data = json.loads(
    #         render_template("Observation", directory="source", params=row)
    #     )
    #
    #     self.update_resource(
    #         "Observation", row["id"], request_data, row["multitenancy"]
    #     )

    # @task
    # @tag("search", "search_observation_subject_value_composite")
    # def search_observation_subject_value_composite(self):
    #     row = self.get_random_observation_row()
    #     code = json.loads(row["code"])["coding"][0]["code"]
    #     value_quantity = row["value_quantity"]
    #     value_concept_coding = row["value_codeable_concept"]
    #
    #     if value_quantity is None:
    #         value_concept_coding = json.loads(value_concept_coding)["coding"][0]
    #         self.search_resource(
    #             "Observation",
    #             f"subject={row['subject']}&code-value-concept={code}${value_concept_coding['system']}|{value_concept_coding['code']}&_count=1",
    #         )
    #     else:
    #         value_quantity = json.loads(value_quantity)
    #         self.search_resource(
    #             "Observation",
    #             f"subject={row['subject']}&code-value-quantity={code}$ge{value_quantity['value']}&_count=1",
    #         )
    #
    # @task
    # @tag("search", "search_organization_by_id")
    # def search_organization_by_id(self):
    #     row = self.get_random_organization_row()
    #     self.search_resource("Organization", f"_id={row['id']}", row["multitenancy"])
    #
    # @task
    # @tag("search", "search_practitioner_by_id")
    # def search_practitioner_by_id(self):
    #     row = self.get_random_practitioner_row()
    #     self.search_resource("Practitioner", f"_id={row['id']}", row["multitenancy"])
    #
    # @task
    # @tag("search", "search_encounter_by_id")
    # def search_encounter_by_id(self):
    #     row = self.get_random_encounter_row()
    #     self.search_resource("Encounter", f"_id={row['id']}", row["multitenancy"])
    #
    # @task
    # @tag("search", "search_condition_by_id")
    # def search_condition_by_id(self):
    #     row = self.get_random_condition_row()
    #     self.search_resource("Condition", f"_id={row['id']}", row["multitenancy"])
    #
    # @task
    # @tag("search", "search_composition_by_id")
    # def search_composition_by_id(self):
    #     row = self.get_random_composition_row()
    #     self.search_resource("Composition", f"_id={row['id']}", row["multitenancy"])


class CustomException(Exception):
    def __init__(self, message, status_code=None):
        super().__init__(message)
        self.status_code = status_code
