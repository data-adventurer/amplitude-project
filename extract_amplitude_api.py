import logging
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
import requests
import json                                                
import zipfile
import gzip
import shutil
import tempfile

# Calculate today's and yesterday's date for the API endpoints
today = datetime.now()
yesterday = today - timedelta(days=1)

# Format start and end times for Amplitude API
start_time = yesterday.strftime('%Y%m%dT00')
end_time = yesterday.strftime('%Y%m%dT23')

# Format the extract date for creating folders
extract_time = yesterday.strftime('%Y%m%d')

base_path = "data"

# Configure logging
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)  # Ensure log directory exists

logging.basicConfig(
    filename=os.path.join(log_dir, f"amplitude_extract_{extract_time}.log"),  # Log file per day
    filemode='a',  # append to file if it exists
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO  # You can change to DEBUG for more verbose logs
)

# Load environment variables from .env file
load_dotenv()

# API URL and parameters
url = 'https://analytics.eu.amplitude.com/api/2/export'
parameters = {
    'start': start_time,
    'end': end_time
}

# Retrieve API credentials from environment variables
api_key = os.getenv('AMP_API_KEY')
secret_key = os.getenv('AMP_SECRET_KEY')
timeout = 10  # request timeout in seconds

# File paths for the zip file and extraction destination
zip_path = os.path.join('zips', extract_time) + '.zip'
destination_path = base_path

# Create a temporary directory for extraction
temp_dir = tempfile.mkdtemp()

# Ensure the destination directory exists
# os.makedirs with exist_ok=True will create the directory if it does not exist
os.makedirs(destination_path, exist_ok=True)
logging.info("Environment Setup: beginning unzip process")

# Make the API request and save response
response = requests.get(url, params=parameters, auth=(api_key, secret_key), timeout=timeout)

# Handle the API response
if response.status_code == 200:
    # print('Successful API call')
    logging.info('Successful API call')

    data = response.content
    with open(zip_path, 'wb') as file:  # save content to zip file
        file.write(data)
else:
    #print(f"Unsuccessful API call! Error {response.status_code}: {response.text}")
    logging.error(f"Unsuccessful API call! Error {response.status_code}: {response.text}")


try:
    # Extract the main zip file into the temporary directory
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(temp_dir)
        logging.info(f"amp_events.zip extracted to temp directory: {temp_dir} ")
except Exception as e:
    logging.error(f"Error extracting zip file: {str(e)}")
    raise

try:
    # Locate the day folder (assumed to be the numeric folder)
    day_folder = next(f for f in os.listdir(temp_dir) if f.isdigit())
    day_path = os.path.join(temp_dir, day_folder)
except Exception as e:
    logging.error(f"Error finding day folder: {str(e)}")
    raise

# Walk through the day folder and decompress each .gz file to the data directory
for root, _, files in os.walk(day_path):
    for file in files:
        if file.endswith('.gz'):
            try:
                gz_path = os.path.join(root, file)
                json_filename = file[:-3]  # Remove .gz extension
                output_path = os.path.join(destination_path, json_filename)

                with gzip.open(gz_path, 'rb') as gz_file, open(output_path, 'wb') as out_file:
                    shutil.copyfileobj(gz_file, out_file)
                
                logging.info(f"Successfully processed: {file} -> {json_filename}")
            except Exception as e:
                logging.error(f"Failed to process file {file}: {str(e)}")

try:
    # Delete the temporary directory
    shutil.rmtree(temp_dir)
    logging.info("Temp directory deleted")

except Exception as e:
    logging.error(f"Failed to delete temp directory: {str(e)}")

print("All files extracted to the 'data' directory!")