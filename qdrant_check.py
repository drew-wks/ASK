from qdrant_client import QdrantClient
import traceback

qdrant_collection_name = "ASK_vectorstore"
QDRANT_URL=os.environ.get("QDRANT_URL"),
QDRANT_API_KEY=os.environ.get("QDRANT_API_KEY"),  # Only required for Qdrant Cloud
    
def qdrant_connect_cloud(QDRANT_API_KEY, QDRANT_URL):
    try:
        print("attempting to assign client")
        client = QdrantClient(
            QDRANT_URL=QDRANT_URL,
            prefer_grpc=True,
            QDRANT_API_KEY=QDRANT_API_KEY,
        )
        return client
    except Exception:
        print("An error occurred while connecting to Qdrant:")
        traceback.print_exc()
        return None


client = qdrant_connect_cloud(QDRANT_API_KEY, QDRANT_URL)
if client:
    try:
        collections = client.get_collections()
        print("Collections:", collections)
    except Exception as e:
        print("An error occurred while getting collections:")
        print(e)