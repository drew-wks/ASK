import os
import traceback
from qdrant_client import QdrantClient
import pprint
import requests


# Checks the status of the Qdrant database.

# To check if it ran correctly, 
#  1. The Requests tab of the Qdrant Cluster Details page should list a request to the /collections/{collection_name} endpoint.
#  2. The Logs tab should have a message related to the collection ace such as "Fetching collection 'ASK_vectorstore'".

# To add an email report of results, implement the code here:
# https://www.youtube.com/watch?v=2OwLb-aaiBQ


url = os.environ.get("QDRANT_URL")
api_key = os.environ.get("QDRANT_API_KEY")  # Only required for Qdrant Cloud

# Function to connect to Qdrant
def qdrant_connect_cloud(api_key, url):
    try:
        print("Attempting to assign client...")
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

# Connect to Qdrant
client = qdrant_connect_cloud(api_key, url)

if client:
    try:
        # Fetching collection information
        collection = client.get_collection('ASK_vectorstore')
        print("Collection name:", 'ASK_vectorstore')
        print("Collection status:", collection.status)
        
        # Pretty print the collection information
        pp = pprint.PrettyPrinter(width=80, compact=False)
        pp.pprint(collection)
        
    except Exception as e:
        print("An error occurred while getting the collection:")
        print(e)


    try:
        response = requests.get(
        f'{url}/metrics', headers={'Authorization': f'Bearer {api_key}'}
        )

        if response.ok:
            for line in response.text.splitlines():
                if 'rest_responses_total' in line or 'grpc_responses_total' in line:
                    print(line)
        else:
            print(f"Failed to fetch metrics: {response.status_code}")
else:
    print("Client is None, unable to proceed.")

