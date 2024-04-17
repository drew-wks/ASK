import os
import traceback
from qdrant_client import QdrantClient
qdrant_collection_name = "ASK_vectorstore"
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
