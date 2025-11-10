# Amplitude Data Export Project

This repository contains a Python script that pulls data from the Amplitude Analytics API, saves it as a `.zip` file, and extracts `.json.gz` files into a local folder for further analysis.

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

## Overview

The script automates the daily export of event data from Amplitude. It:

1. Calculates timestamps for the previous day's data.
2. Calls the Amplitude Export API using credentials from a `.env` file.
3. Saves the API response as a ZIP file.
4. Extracts `.json.gz` files from the ZIP into a date-specific folder (e.g., `data/YYYYMMDD/`).
5. Logs all steps, warnings, and errors into a daily log file.

![Data Flow Diagram](iimages/Extracting Cycle.png)

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

2. Create and activate a virtual environment:

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

```bash
AMP_API_KEY=your_api_key
AMP_SECRET_KEY=your_secret_key
```

## Usage

- Ensure your .env file contains valid Amplitude API credentials.
- The `.zip` file will be saved in the cloned repository
- Extracted .json.gz files will be saved under a date-specific folder: data/YYYYMMDD/.
- Logs will be saved under data/logs/amplitude_extract_YYYYMMDD.log.

## File Structure

```bash
After running the script, the project folder will look like this:
amplitude-project/
├── extract_amplitude_api.py # Main Python script
├── .env # Environment file with API credentials
├── data.zip # ZIP downloaded from the API
├── data/
│ ├── YYYYMMDD/ # Folder for each day's extracted files
│ │ ├── events1.json.gz
│ │ ├── events2.json.gz
│ │ └── ...
│ └── logs/
│ └── amplitude_extract_YYYYMMDD.log
└── requirements.txt # Required Python packages
```

---

## Error Handling

- If the API call fails, the script prints the HTTP status code and error text.
- If the downloaded `.zip` file is corrupted or invalid, a `BadZipFile` error is printed.
- Any other unexpected errors are caught and displayed for debugging.

---

## Notes

- The script only extracts files ending with `.json.gz` and ignores other file types.
- Files are not overwritten if they already exist in the destination folder.
- The script is designed to run daily but can be executed manually at any time.
- All operations are logged with timestamps and severity levels (INFO, WARNING, ERROR, EXCEPTION).
- Daily logs are saved in data/logs/ with the format: amplitude_extract_YYYYMMDD.log.
- Logging replaces print() statements for better monitoring and troubleshooting.
