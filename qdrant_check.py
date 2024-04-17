import os
import traceback
from qdrant_client import QdrantClient


url=os.environ.get("QDRANT_URL")
api_key=os.environ.get("QDRANT_API_KEY")  # Only required for Qdrant Cloud
    
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


client = qdrant_connect_cloud(api_key, url)
if client:
    try:
        collection = client.get_collection('ASK_vectorstore')
        print("Collection name:", 'ASK_vectorstore')
        print("Collection status:", collection.status)
    except Exception as e:
        print("An error occurred while getting collections:")
        print(e)
