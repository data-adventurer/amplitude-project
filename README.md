# Amplitude Data Export Project

This repository is dedicated to the Amplitude pipeline project that goes through the fundamental stpes of the data engineering lifecycle. The first part focused on extracting data, the second part looks into loading that data into an S3 bucket.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [File Structure](#file-structure)
- [Error Handling](#error-handling)
- [Logging](#logging)
- [Notes](#notes)

---

## Background

Airbyte vs Python

<img src="https://github.com/data-adventurer/amplitude-project/blob/main/images/Pipeline.png?raw=true">

## Overview

The script automates the daily export of event data from Amplitude. It:

1. Calculates timestamps for the previous day's data.
2. Calls the Amplitude Export API using credentials from a `.env` file.
3. Saves the API response as a ZIP file.
4. Extracts `.json.gz` files from the ZIP into a date-specific folder (e.g., `data/YYYYMMDD/`).
5. Logs all steps, warnings, and errors into a daily log file.

<img src="https://github.com/data-adventurer/amplitude-project/blob/main/images/ExtractingCycle.png?raw=true">

---

## Features

- Automatically calculates start and end timestamps for the previous day.
- Extracts `.json.gz` files from nested directories in the `.zip` file.
- Prevents overwriting files that already exist.
- Logs successful extractions, skipped files, API errors, and ZIP issues.
- Handles API failures and corrupted ZIP files gracefully.

---

## Installation

1. Clone this repository:

```bash
git clone https://github.com/yourusername/amplitude-project.git
```

2. Create a branch

```bash
git checkout -b your-branch-name
```

3. Create and activate a virtual environment:

```bash
python -m venv .venv
# Linux / Mac
source .venv/bin/activate
# Windows
.venv\Scripts\activate
```

3. Install required packages

```bash
pip install -r requirements.txt
```

4. Add a .env file in the root of the project containing your Amplitude credentials:

```
AMP_API_KEY=your_api_key
AMP_SECRET_KEY=your_secret_key
```

---

## Setting up Airbyte

---

## Setting up AWS

### Requirements

1. Account
2. Key
3. Bucket
4. User
5. Policies

```python
aws_access_key = os.getenv('aws_access_key')
aws_secret_key = os.getenv('aws_secret_access_key')
aws_bucket = os.getenv('aws_bucket')

# Create S3 Client using AWS Credentials
s3_client = boto3.client(
    's3',
    aws_access_key_id=aws_access_key,
    aws_secret_access_key=aws_secret_key
)
```

---

## Setting up Snowflake

1. Connect to AWS
2. Storage Integration

   ```sql
   CREATE OR REPLACE STORAGE INTEGRATION lf_amplitude_python_import
   TYPE = EXTERNAL_STAGE
   STORAGE_PROVIDER = 'S3'
   ENABLED = TRUE
   STORAGE_AWS_ROLE_ARN = 'arn:aws:iam::xxxx:role/bucket'
   STORAGE_ALLOWED_LOCATIONS = ('s3://bucket/directory/');
   ```

3. Stage
   ```sql
   CREATE OR REPLACE STAGE lf_amplitude_python_stage
   STORAGE_INTEGRATION = lf_amplitude_python_import
   URL = 's3://bucket/directory/'
   FILE_FORMAT = lorrainef_json_format;
   ```

---

## How the code works

### Extract

- Ensure your .env file contains valid Amplitude API credentials.
- The `.zip` file will be saved in the cloned repository
- Extracted .json.gz files will be saved under a date-specific folder: data/YYYYMMDD/.
- Logs will be saved under data/logs/amplitude_extract_YYYYMMDD.log.

#### Error Handling

- If the API call fails, the script prints the HTTP status code and error text.
- If the downloaded `.zip` file is corrupted or invalid, a `BadZipFile` error is printed.
- Any other unexpected errors are caught and displayed for debugging.

---

### Load

This code looks through a folder on your computer, finds all the JSON files, uploads them to a specific folder in an Amazon S3 cloud storage bucket, and then deletes the copies from your computer once the upload is successful.

<img src="https://github.com/data-adventurer/amplitude-project/blob/main/images/Loading%20Cycle.png?raw=true">

```python
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

```

#### Error Handling

- The code checks for problems each time it tries to upload a file.
- If something goes wrong (like no internet connection or missing permissions), the code doesn’t stop running.
- Instead, it skips the failed upload and moves on to the next file.
- It prints a message showing which file caused the error and what went wrong.
- This helps you identify and fix issues later without having to restart the entire process.

## File Structure

---

## Notes

- The script only extracts files ending with `.json.gz` and ignores other file types.
- Files are not overwritten if they already exist in the destination folder.
- The script is designed to run daily but can be executed manually at any time.
- All operations are logged with timestamps and severity levels (INFO, WARNING, ERROR, EXCEPTION).
- Daily logs are saved in data/logs/ with the format: amplitude_extract_YYYYMMDD.log.
- Logging replaces print() statements for better monitoring and troubleshooting.
