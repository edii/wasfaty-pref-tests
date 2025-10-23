import boto3
import json
from botocore.exceptions import ClientError
from botocore.config import Config


class S3:
    def __init__(self, aws_profile: str):
        self.aws_session = boto3.Session(profile_name=aws_profile)
        self.client = self.aws_session.client(
            "s3", config=Config(signature_version="v4", region_name="eu-north-1")
        )

    def list_s3_directory(self, bucket, prefix):
        response = self.client.list_objects_v2(Bucket=bucket, Prefix=prefix)
        if response["ResponseMetadata"]["HTTPStatusCode"] == 200:
            if "Contents" in response:
                return [obj["Key"] for obj in response["Contents"]]
        else:
            raise f"Invalid s3 response: {response}"

    def get_json_object(self, bucket, key):
        response = self.client.get_object(Bucket=bucket, Key=key)
        return json.loads(response["Body"].read().decode("utf-8"))

    def get_object_stream(self, bucket, key):
        response = self.client.get_object(Bucket=bucket, Key=key)
        return response["Body"]

    def get_object_size(self, bucket, key):
        response = self.client.head_object(Bucket=bucket, Key=key)
        return response["ContentLength"]

    def try_get_object_size(self, bucket, key):
        try:
            response = self.client.head_object(Bucket=bucket, Key=key)
            return response["ContentLength"]
        except ClientError as e:
            if e.response["Error"]["Code"] == "404":
                return None
            else:
                raise e

    def get_presigned_url(self, bucket, key):
        try:
            url = self.client.generate_presigned_url(
                "get_object",
                Params={"Bucket": bucket, "Key": key},
            )
            return url
        except ClientError as e:
            raise f"Failed to create presigned url: {e}"
