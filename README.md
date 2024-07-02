# GCS Bucket Metrics Fetcher

This script collects various metrics from Google Cloud Storage buckets over the past month and generates a CSV report. The metrics include request counts, network sent/received bytes, storage total bytes, and object counts.

## Prerequisites

- Python 3.6 or higher
- Google Cloud SDK
- `pandas` library
- Google Cloud credentials

## Installation

1. **Clone the repository:**
   ```
   git clone https://github.com/your-username/gcs-metrics-fetcher.git
   cd gcs-metrics-fetcher
    ```

2. Install the required Python packages

```
pip install pandas google-cloud-storage google-cloud-monitoring
```

3. Set up Google Cloud authentication
- Download your service account key JSON file from Google Cloud Console.
- Set the GOOGLE_APPLICATION_CREDENTIALS environment variable to the path of your service account key JSON file
```
export GOOGLE_APPLICATION_CREDENTIALS_PATH=~/path-to-your-service-account-key.json
```

## Usage

1. Run the script
```
./gcs-metrics-fetcher.py
```

2. Output
- The script will generate a CSV file named gcs-bucket-metrics-<project_id>.csv containing the collected metrics.

## Script Details
The script performs the following tasks:
1. Setup
- Sets up Google Cloud authentication using the provided service account key.
- Initializes the Google Cloud Storage and Monitoring clients.

2. Define the time range
- Collects metrics for the past month.

3. Fetch metrics
- Retrieves various metrics for each bucket in the project:
    - Request count
    - Network sent bytes
    - Network received bytes
    - Storage total bytes
    - Object count

4. Calculate statistics
- For each metric, calculates total, average, maximum, minimum, standard deviation, and percent change values.

5. Generate CSV report
- Compiles the collected data into a pandas DataFrame.
- Saves the DataFrame to a CSV file.

## Customization

- Metrics to fetch
    - The script fetches specific metrics using the `fetch_metrics` function. You can customize the metrics by modifying the `metric_type` parameters in the script.

- Commented out metrics
    - Some metrics calculations are commented out for future reference. Uncomment the relevant lines if needed.

## Error Handling
The script includes basic error handling to catch and print any errors encountered while fetching metrics.

## Example
The generated CSV file will contain columns such as:

- bucket_name
- region
- project_id
- request_total
- request_percent_change
- sent_total
- sent_percent_change
- received_total
- received_percent_change
- total_GB_latest
- total_bytes_percent_change
- total_objects_total
- total_objects_percent_change
