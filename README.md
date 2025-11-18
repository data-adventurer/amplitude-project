# Amplitude Data Export Project

This repository is dedicated to the Amplitude pipeline project that goes through the fundamental steps of the data engineering lifecycle. The first part focused on extracting data, the second part looks into loading that data into an S3 bucket.

---

## Background

Airbyte vs Python

<img src="https://github.com/data-adventurer/amplitude-project/blob/main/images/Pipeline.png?raw=true">

---

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

## Setting up the Repository

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

## Setting up Airbyte

## Setting up AWS

---

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

Follow these instructions to set up Snowflake for your data transformation process. Be sure to replace all placeholder text (inside angle brackets <>) with your own information.

1. Connect to your cloud storage provider

First, make sure Snowflake can communicate with your cloud storage (such as AWS S3). This usually requires setting up a storage integration.

2. Create a storage integration

Run the following SQL to create a storage integration. Replace <integration_name>, <provider_name>, <arn_value>, and <bucket_or_path> with your own values.

```sql
create or replace storage integration <integration_name>
    type = external_stage
    storage_provider = '<provider_name>'  -- for example, 's3'
    enabled = true
    storage_aws_role_arn = '<arn_value>'
    storage_allowed_locations = ('<bucket_or_path>')
```

3. Create a stage

Use this SQL to create a stage associated with your storage integration. Replace <stage_name>, <integration_name>, <storage_path>, and <file_format_name> accordingly.

```sql
create or replace stage <stage_name>
    storage_integration = <integration_name>
    url = '<storage_path>'  -- for example, 's3://my-bucket/folder/'
    file_format = <file_format_name>
```

4. Create a pipe

The pipe automatically loads data from the stage into your target table. Update <pipe_name>, <target_table>, <stage_name>, and <file_format_name> for your environment.

```sql
create or replace pipe <pipe_name>
    auto_ingest = true
    as
    copy into <target_table>
    from @<stage_name>
    file_format = (format_name = <file_format_name>)
    match_by_column_name = case_insensitive
    on_error = 'continue'
```

5. Create a stream

The stream captures changes on your source table for incremental processing. Replace <stream_name> and <source_table> as needed.

```sql
create or replace stream <stream_name>
on table <source_table>
```

---

## How the process works

### Extract with Python Code

- Ensure your .env file contains valid Amplitude API credentials.
- The `.zip` file will be saved in the cloned repository
- Extracted .json.gz files will be saved under a date-specific folder: data/YYYYMMDD/.
- Logs will be saved under data/logs/amplitude_extract_YYYYMMDD.log.

#### Error Handling

- If the API call fails, the script prints the HTTP status code and error text.
- If the downloaded `.zip` file is corrupted or invalid, a `BadZipFile` error is printed.
- Any other unexpected errors are caught and displayed for debugging.

### Load with Python Code

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

#### Notes

- The script only extracts files ending with `.json.gz` and ignores other file types.
- Files are not overwritten if they already exist in the destination folder.
- The script is designed to run daily but can be executed manually at any time.
- All operations are logged with timestamps and severity levels (INFO, WARNING, ERROR, EXCEPTION).
- Daily logs are saved in data/logs/ with the format: amplitude_extract_YYYYMMDD.log.
- Logging replaces print() statements for better monitoring and troubleshooting.

### Orchestrate with Snowflake

At a high level, the reasoning for this Snowflake data model and workflow comes from the specific marketing questions the team needs to answer. This led to careful planning of the schema, focusing on how data flows from raw events to consumable tables that enable analytics. The tables themselves were built in Snowflake, and SQL procedures were set up to automate the transformation steps, with future improvements planned around automating the scheduling of these processes.

Below, each major procedure and step is explained in plain language, describing its purpose and how it fits into the overall bronze (raw), silver (cleansed/structured), and analytic (fact/dimensional) layer approach to building out a marketing data foundation.

#### Streaming and Ingesting Raw Data (Bronze Layer)

- **the pipe**  
  The pipe enables automated, continuous loading (called "auto_ingest") of JSON event files from the cloud staging area into the raw events table. This means as soon as new event data lands in cloud storage, Snowflake ingests it, making near-real-time analytics possible .

#### Building and Populating the Bronze Tables

- **amplitude_base_levels()**  
  This procedure is the main logic for extracting, cleaning, and shaping the raw event data into a series of more usable, structured tables. The goal here is to take the raw JSON records and break out key fields, then further flatten and organize the semi-structured information for downstream use .

  **Step-by-step inside the procedure:**

  - Data is first inserted into a base table with fields extracted from the JSON data (such as IDs, event types, device information, and timestamps).
  - Nested event properties are flattened into key-value pairs in a new table, making each event property accessible as an individual row.
  - Nested user properties are also flattened in a similar manner.
  - Specific page- and referrer-related fields are further pivoted into columns for easier querying by later analytics (e.g., supporting analysis of session sources, behaviors, and page navigation).

#### Creating Silver/Analytic Tables (Facts & Dimensions)

- **amplitude_dim_fact()**  
  This procedure transforms the staged, cleansed data into analytic-ready tables:
  - A user dimension table (`amplitude_dim_user`) is built with information about devices, geography, and user traits.
  - A page dimension table (`amplitude_dim_page`) is created, assigning unique page IDs and consolidating different page attributes.
  - An event fact table (`amplitude_fact_event`) is constructed, linking events to pages and to referrer details so that analysis can group and segment event behaviors.
  - A session fact table (`amplitude_fact_session`) summarizes session boundaries (start/end times), session length, and number of events, giving marketers valuable insights about user engagement durations and activities .

#### Orchestrating the Workflow

- **procedure amplitude_data()**  
  This is an orchestrator procedure that simply calls the two transformation procedures above in order—so all the tables are refreshed in sequence with a single call .

- **call amplitude_data();**  
  Executes the entire data transformation pipeline in order. In future improvements, a Snowflake task will be used to schedule this step automatically at regular intervals, taking human intervention out of the pipeline .

This approach lays down a clear, repeatable path for transforming semi-structured event data for marketing analytics—from initial raw ingest in the bronze layer, through structuring/cleansing in the silver layer, all the way to well-organized analytic tables powering data-driven marketing decisions .

### Next Steps & Future Considerations

**Task Automation:**  
A key next step is setting up Snowflake tasks to schedule the transformation procedures at regular intervals (e.g., hourly or daily). This automation will ensure that data is ingested and processed on a consistent schedule, making your reporting as close to real-time as needed without manual intervention .

**Handling Duplicates and Incremental Loads:**  
Modify the current procedures or table structures to properly handle duplicate records. This typically means adding logic to the transformation code to deduplicate new data as it is loaded, using unique keys or timestamps. Also, tables should be updated incrementally: only new or changed data is processed, reducing unnecessary computation and ensuring efficiency .

**Preserving Historical Data:**  
Carefully build your tables to keep full historical records, rather than overwriting existing data. Consider using append-only tables or slowly changing dimension (SCD) techniques if you need to track how user or session information changes over time .

**Views vs. Tables:**  
Consider whether some outputs should be implemented as views (which reflect real-time data) versus physical tables (which store point-in-time snapshots). Views can simplify model maintenance, while tables support historical audits and time-based performance .

**Dynamic SQL Usage:**  
Using dynamic SQL can make your procedures more flexible and adaptable to changing schemas or new requirements, but also introduces complexity and potential risk. Balance flexibility with maintainability when deciding to implement dynamic SQL in transformation procedures .

#### Potential Future Improvements

- **Create a dedicated location dimension table** to enhance geographic analyses and allow marketers to drill down by region, city, or store location.
- **Include user email addresses** (if compliant with privacy rules) to support direct marketing campaigns and communication analysis.
- **Expand the marketing use case** to systematically identify website issues (such as high-exit pages or error events), guiding product and engineering teams.
- **Build campaign attribution logic** to pinpoint which marketing campaigns or channels are generating higher foot traffic or engagement, closing the loop from digital marketing to tangible results.

By iteratively improving automation, data model sophistication, and analytic scope, this Snowflake setup will continue to power robust, actionable marketing analytics as the needs of the business evolve .
