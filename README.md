# kodjin.perf_tests

### Installation
1. Install [uv](https://docs.astral.sh/uv/getting-started/installation/)
2. Install python:
    `uv python install 3.13`
3. Activate it:
    `uv python pin 3.13`
4. Sync `uv` environment:
    `uv sync`
5. Configure your IDE to use `ruff` formatter (e.g. [Visual Studio extension](https://marketplace.visualstudio.com/items?itemName=charliermarsh.ruff))
6. Run tests:
    `uv run locust`

### Test plan for perfomance testing
Before run tests need to scale fhir-server-fixtures-worker, fhir-server-search-fixtures-worker, fhir-terminology-fixtures-worker to 0

### Prepare data for testing
1. Configure aws cli with access to s3 bucket with synthea data:
    - get temporary aws access key id, secret key, session token with command `aws sts get-session-token --serial-number {arn} --token-code {code}` where `arn` is your user's `arn` (e.g. `arn:aws:iam::{user_id}:mfa/{username}`)
     and `code` is your two factor code (which is generated each minute)
    - set aws access key id for profile (`mfa` as example): `aws configure set aws_access_key_id {access_key_id} --profile mfa`
    - set aws secret access key for the same profile: `aws configure set aws_secret_access_key {aws_secret_access_key} --profile mfa`
    - set aws session token for the same profile: `aws configure set aws_session_token {aws_session_token} --profile mfa`
2. Disable fixture workers
3. Upload extensions:
    - switch to virtualenv (if not did before):
     `source env/bin/activate.fish`
    - execute script: `HOST={HOST} uv run -m scripts.synthea_upload_extensions` where HOST - is your cluster's host
4. Create import for required resource:
    `HOST=https://kodjin-ffs-31322.edenlab.dev uv run -m scripts.synthea_create_import` where HOST - is your cluster's host




### POST resources
Tags
    `patient`
    `medication`
    `coverage`
    `explanationOfBenefit`
    `observation`

### POST transactions / batch
1. Transactin Location without reference
    `location_transaction_10`
    `location_transaction_50`
    `location_transaction_100`
2. Transactin Claim with relative references
    `claim_reference_transaction_100`
    `claim_reference_transaction_50`
    `claim_reference_transaction_10`
3. Batch Location without reference
    `location_batch_100`
    `location_batch_50`
    `location_batch_10`
4. Batch Claim with relative reference
    `claim_reference_batch_100`
    `claim_reference_batch_50`
    `claim_reference_batch_10`

### Search
Run this tag `precondition_search`, to generate patients with different values (`precondition_sd` must also be run, to create 10 StructureDefinitons)

### Search patient

1. Search patient by POST _id `search_post_id_patient`
{url}/fhir/{resourceType}/_search?_id={random_id}
2. Search patient by GET id `search_post_id_patient`
{url}/fhir/{resourceType}/{random_id}
3. Search patient by POST source `search_post_source_patient`
{url}/fhir/{resourceType}/_search?_source={random_source}
4. Search patient by POST profile `search_post_profile_patient`
{url}/fhir/{resourceType}/_search?_profile={random_profile}
5. Search patient by GET gender `search_post_gender_patient`
{url}/fhir/{resourceType}/_search?_gender={random_gender}
6. Search patient by GET family `search_post_name_patient`
{url}/fhir/{resourceType}/_search?_family={random_last_name}
7. Search patient by GET given and gender `search_post_name_gender_patient`
{url}/fhir/{resourceType}/_search?_given={random_name}&gender={random_gender}
8. Search patient by GET city and gender `search_post_city_gender_patient`
{url}/fhir/{resourceType}/_search?_address-city={random_city}&gender={random_gender}

### Search terminology (validate, expand, translate)
1. Search ValueSet GET by validate-code `search_terminology_validate_code`
{host}/terminology/ValueSet/$validate-code?system={system}
2. Search ValueSet GET by expand `search_terminology_expand`
{host}/terminology/ValueSet/icd-10-test/$expand?filter=A00
3. Search ValueSet GET by translate `search_terminology_expand`
{host}/terminology/ConceptMap/$translate?url={url}

### Search new terminology
1. Search ValueSet by GET name `search_terminology_string_valueSet`
{host}/terminology/ValueSet?name=ActionPrecheckBehavior
2. Search CodeSystem by GET url `search_terminology_url_version_codeSystem`
{host}/terminology/CodeSystem?url={code_system_url}|4.0.1
3. Search CodeSystem by GET context-type `search_terminology_token_codeSystem`
{host}/terminology/CodeSystem?context-type={code_system_url}|species
4. Search CodeSystem by GET supplements `search_terminology_reference_codeSystem`
{host}/terminology/CodeSystem?supplements={code_system_url}
5. Search CodeSystem by GET date `search_terminology_date_codeSystem`
{host}/terminology/CodeSystem?date=lt2023-12-04T10:00:00&_skip=20
6. Search CodeSystem by GET condext-quantity `search_terminology_quantity_codeSystem`
{host}/terminology/CodeSystem?context-quantity=le2|{code_system_url}|m
7. Search CodeSystem by GET context-type-value `search_terminology_composite_codeSystem`
{{host}}/terminology/CodeSystem?context-type-value={code_system_url}|337915000
8. Search CodeSystem by GET lastUpdated `search_terminology_lastupdated`
{host}/terminology/CodeSystem?context-type={code_system_url}|species&name=Code system summary example&_lastUpdated=ge2024-04-29
9. Search CodeSystem by GET sort `search_terminology_count_last`
{host}/terminology/CodeSystem?_sort=-_lastUpdated&_count=1
10. Search CodeSystem by GET count `search_terminology_count_page`
{host}/terminology/CodeSystem?_count=1&_sort=_lastUpdated&_page=5

### Bulk-export
1. Run this tag `precondition_bulk_export_all` for generate all types resources and send GET request  {url}/fhir/$export
2. Run this tag `precondition_bulk_export_patient` for generate all patient-specific resources and send GET request {url}/fhir/Patient/$export

### Bulk-import
1. Use python script to generate ndjson file `python3 parser.py `
2. Before run script need to create `organization`, `practitioner`, `coverage`, `patient` and set their values (id, identifier) to dict dict_for_ndjson_file in parser.py file
3. Upload ndjson file to minio. Get share link
4. Change ALLOWED_FILE_HOST_REGEX to `'.+'` in fhir-server-import-processor

### Other tests
1. Post CodeSystem `post_code_system`
