#! /usr/bin/env python3

import os
from datetime import datetime, timedelta
import pandas as pd
from google.cloud import storage, monitoring_v3

# Fetch the local environment variable
credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS_PATH', '~/default/path/to/credentials.json')

# Set up authentication
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path

# Initialize clients
storage_client = storage.Client()
monitoring_client = monitoring_v3.MetricServiceClient()

# Time range for the past month
end_time = datetime.utcnow()
start_time = end_time - timedelta(days=30)

# Function to fetch metrics
def fetch_metrics(bucket_name, metric_type, aligner):
    project_id = storage_client.project
    project_name = f"projects/{project_id}"

    interval = monitoring_v3.TimeInterval({
        "end_time": {"seconds": int(end_time.timestamp()), "nanos": end_time.microsecond * 1000},
        "start_time": {"seconds": int(start_time.timestamp()), "nanos": start_time.microsecond * 1000},
    })

    filter_query = f'metric.type="{metric_type}" AND resource.type="gcs_bucket" AND resource.labels.bucket_name="{bucket_name}"'

    aggregation = monitoring_v3.Aggregation(
        alignment_period={"seconds": 86400},  # Align data points to 1 day intervals
        per_series_aligner=aligner
    )

    try:
        results = monitoring_client.list_time_series(
            request={
                "name": project_name,
                "filter": filter_query,
                "interval": interval,
                "view": monitoring_v3.ListTimeSeriesRequest.TimeSeriesView.FULL,
                "aggregation": aggregation,
            }
        )

        values = []
        for result in results:
            for point in result.points:
                values.append(point.value.double_value)

        if values:
            total_value = sum(values)
            average_value = total_value / len(values)
            max_value = max(values)
            min_value = min(values)
            stddev_value = pd.Series(values).std()
            percent_change = ((values[-1] - values[0]) / values[0]) * 100 if values[0] != 0 else 0
            latest_value = values[-1]  # Latest value in the series
        else:
            total_value = average_value = max_value = min_value = stddev_value = percent_change = latest_value = 0

    except Exception as e:
        print(f"Error fetching metrics for bucket {bucket_name}, metric {metric_type}: {e}")
        total_value = average_value = max_value = min_value = stddev_value = percent_change = latest_value = 0

    return total_value, average_value, max_value, min_value, stddev_value, percent_change, latest_value

# Collect data
data = []
project_id = storage_client.project  # Get the project ID

for bucket in storage_client.list_buckets():
    bucket_name = bucket.name
    bucket_region = bucket.location

    # Fetch metrics
    request_total, request_avg, request_max, request_min, request_stddev, request_percent_change, _ = fetch_metrics(bucket_name, 'storage.googleapis.com/api/request_count', monitoring_v3.Aggregation.Aligner.ALIGN_RATE)
    sent_total, sent_avg, sent_max, sent_min, sent_stddev, sent_percent_change, _ = fetch_metrics(bucket_name, 'storage.googleapis.com/network/sent_bytes_count', monitoring_v3.Aggregation.Aligner.ALIGN_RATE)
    received_total, received_avg, received_max, received_min, received_stddev, received_percent_change, _ = fetch_metrics(bucket_name, 'storage.googleapis.com/network/received_bytes_count', monitoring_v3.Aggregation.Aligner.ALIGN_RATE)
    _, _, _, _, _, total_bytes_percent_change, total_bytes_latest = fetch_metrics(bucket_name, 'storage.googleapis.com/storage/total_bytes', monitoring_v3.Aggregation.Aligner.ALIGN_MEAN)
    total_objects_total, total_objects_avg, total_objects_max, total_objects_min, total_objects_stddev, total_objects_percent_change, _ = fetch_metrics(bucket_name, 'storage.googleapis.com/storage/object_count', monitoring_v3.Aggregation.Aligner.ALIGN_MEAN)

    # Convert total_bytes_latest from bytes to terabytes
    total_GB_latest = total_bytes_latest / (1024 ** 3)

    data.append({
        "bucket_name": bucket_name,
        "region": bucket_region,
        "project_id": project_id,
        "request_total": request_total,
        # "request_avg": request_avg,  # Commented out for future reference
        # "request_max": request_max,  # Commented out for future reference
        # "request_min": request_min,  # Commented out for future reference
        # "request_stddev": request_stddev,  # Commented out for future reference
        "request_percent_change": request_percent_change,
        "sent_total": sent_total,
        # "sent_avg": sent_avg,  # Commented out for future reference
        # "sent_max": sent_max,  # Commented out for future reference
        # "sent_min": sent_min,  # Commented out for future reference
        # "sent_stddev": sent_stddev,  # Commented out for future reference
        "sent_percent_change": sent_percent_change,
        "received_total": received_total,
        # "received_avg": received_avg,  # Commented out for future reference
        # "received_max": received_max,  # Commented out for future reference
        # "received_min": received_min,  # Commented out for future reference
        # "received_stddev": received_stddev,  # Commented out for future reference
        "received_percent_change": received_percent_change,
        "total_GB_latest": total_GB_latest,
        # "total_bytes_avg": total_bytes_avg,  # Commented out for future reference
        # "total_bytes_max": total_bytes_max,  # Commented out for future reference
        # "total_bytes_min": total_bytes_min,  # Commented out for future reference
        # "total_bytes_stddev": total_bytes_stddev,  # Commented out for future reference
        "total_bytes_percent_change": total_bytes_percent_change,
        "total_objects_total": total_objects_total,
        # "total_objects_avg": total_objects_avg,  # Commented out for future reference
        # "total_objects_max": total_objects_max,  # Commented out for future reference
        # "total_objects_min": total_objects_min,  # Commented out for future reference
        # "total_objects_stddev": total_objects_stddev,  # Commented out for future reference
        "total_objects_percent_change": total_objects_percent_change
    })

# Create DataFrame
df = pd.DataFrame(data)

# Save to CSV
df.to_csv('gcs-bucket-metrics-' + project_id + '.csv', index=False)

print("Metrics have been successfully written to gcs_bucket_metrics.csv")
