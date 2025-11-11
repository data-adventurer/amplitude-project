import os
import boto3
from dotenv import load_dotenv

load_dotenv()

aws_access_key = os.getenv('aws_access_key')
aws_secret_key = os.getenv('aws_secret_access_key')
aws_bucket = os.getenv('aws_bucket')

# Create S3 Client using AWS Credentials
s3_client = boto3.client(
    's3',
    aws_access_key_id=aws_access_key,
    aws_secret_access_key=aws_secret_key
)

dir_path = "data"  # folder with all your json files

# List all JSON files directly in the data directory
files_to_upload = [f for f in os.listdir(dir_path) if f.endswith(".json")]

for file in files_to_upload:
    file_path = os.path.join(dir_path, file)
    aws_file_destination = f"python-import/{file}"  # S3 key (path inside the bucket)

    try:
        s3_client.upload_file(file_path, aws_bucket, aws_file_destination)
        print(f"✓ Uploaded: {file}")

        # Delete the local file after successful upload
        os.remove(file_path)
        print(f"Deleted: {file}")

    except Exception as e:
        print(f"Error uploading {file}: {e}")