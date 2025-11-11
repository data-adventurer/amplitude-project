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

# List all JSON files directly in the specified data directory
files_to_upload = [f for f in os.listdir(dir_path) if f.endswith(".json")]

# Loop through each JSON file and upload it to the specified AWS S3 bucket
for file in files_to_upload:
    # Construct the full local path to the file
    file_path = os.path.join(dir_path, file)
    
    # Define the destination path (S3 key) inside the bucket
    aws_file_destination = f"python-import/{file}"

    try:
        # Upload the file to S3
        s3_client.upload_file(file_path, aws_bucket, aws_file_destination)
        print(f"✓ Uploaded: {file}")

        # Delete the local file after a successful upload to free up space
        os.remove(file_path)
        print(f"Deleted: {file}")

    except Exception as e:
        # Catch and print any errors that occur during upload or deletion
        print(f"Error uploading {file}: {e}")
