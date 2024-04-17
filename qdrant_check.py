import os
from qdrant_client import QdrantClient
import traceback
import requests  # Import requests library to make HTTP requests


url = os.environ.get("QDRANT_URL")
api_key = os.environ.get("QDRANT_API_KEY")  # Only required for Qdrant Cloud



def qdrant_connect_cloud(api_key, url):
    try:
        print("attempting to assign client")
        client = QdrantClient(
            url=url,
            prefer_grpc=True,
            api_key=api_key,
        )
        return client
    except Exception:
        print("An error occurred while connecting to Qdrant:")
        traceback.print_exc()
        return None



# Function to fetch total gRPC responses from Qdrant server metrics
def fetch_grpc_responses_total():
    try:
        headers = {"Authorization": f"Bearer {api_key}"}
        response = requests.get(f"{url}/metrics", headers=headers)
        if response.status_code == 200:
            lines = response.text.split("\n")
            # Find the line containing the grpc_responses_total metric
            for line in lines:
                if line.startswith("grpc_responses_total"):
                    # Split line into metric name and value
                    metric_name, metric_value = line.split(" ")
                    grpc_responses_total = int(metric_value)
                    return grpc_responses_total
            return None
        else:
            print(
                f"Failed to fetch metrics: {response.status_code} {response.reason}")
            return None
    except Exception as e:
        print(f"An error occurred while fetching metrics: {e}")
        return None



# Connect to Qdrant server
client = qdrant_connect_cloud(api_key, url)
if client:
    try:
        collections = client.get_collections()
        print("Collections:", collections)
    except Exception as e:
        print("An error occurred while getting collections:")
        print(e)

    # Fetch total gRPC responses
    grpc_responses_total = fetch_grpc_responses_total()
    if grpc_responses_total is not None:
        print("Total gRPC responses:", grpc_responses_total)
    else:
        print("Failed to fetch total gRPC responses")
