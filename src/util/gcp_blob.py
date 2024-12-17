import json
from typing import Union
from google.cloud import storage
from google.cloud.storage import Client
from io import BytesIO
import os
from google.auth import exceptions
from google.oauth2 import service_account

# Initialize the GCS client


def get_gcp_blob_client() -> Client:
    credentials_json = os.getenv('CREDENTIAL_JSON')

    if not credentials_json:
        raise exceptions.DefaultCredentialsError(
            "The GOOGLE_APPLICATION_CREDENTIALS_JSON environment variable is not set.")

    credentials_info = json.loads(credentials_json)

    credentials = service_account.Credentials.from_service_account_info(
        credentials_info)

    return storage.Client(credentials=credentials)


def upload_json_to_blob(bucket_name: str, data: Union[list, dict], destination_blob_name: str):
    """Uploads in-memory data to Google Cloud Storage as a JSON file."""
    # Initialize a client
    storage_client = get_gcp_blob_client()

    # Reference to the bucket
    bucket = storage_client.get_bucket(bucket_name)

    # Create a blob object for the destination file
    blob = bucket.blob(destination_blob_name)

    # Convert the data to a JSON string and write to memory buffer
    json_data = json.dumps(data)
    memory_buffer = BytesIO(json_data.encode('utf-8'))

    # Upload the in-memory file to GCS
    blob.upload_from_file(memory_buffer, content_type='application/json')

    print(f"JSON data uploaded to {destination_blob_name}.")


def read_json_from_blob(bucket_name: str, destination_blob_name: str) -> Union[list, dict]:
    # Initialize a client
    storage_client = get_gcp_blob_client()

    # Reference to the bucket
    bucket = storage_client.get_bucket(bucket_name)

    # Create a blob object for the destination file
    blob = bucket.blob(destination_blob_name)
    content = blob.download_as_text()
    return json.loads(content)
