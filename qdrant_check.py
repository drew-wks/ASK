import os
import traceback
from qdrant_client import QdrantClient
import pprint

'''
Checks the status of the Qdrant database.

To check if it ran correctly, 
1. The Requests tab of the Qdrant Cluster Details page should list a request to the /collections/{collection_name} endpoint.
2. The Logs tab should have a message related to the collection ace such as "Fetching collection 'ASK_vectorstore'".

To add an email report of results, implement the code here:
https://www.youtube.com/watch?v=2OwLb-aaiBQ
'''

# Fetching environment variables
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
else:
    print("Client is None, unable to proceed.")
