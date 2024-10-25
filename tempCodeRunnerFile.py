def get_retriever():
    '''Creates and caches the document retriever and Qdrant client.'''

    client = QdrantClient(
        url=st.secrets["QDRANT_URL"], 
        prefer_grpc=True, 
        api_key=st.secrets["QDRANT_API_KEY"]
    )  # cloud instance
    # client = QdrantClient(path="/tmp/local_qdrant" )  # local instance: /private/tmp/local_qdrant

    qdrant = Qdrant(
        client=client,
        collection_name=qdrant_collection_name,
        embeddings=config["embedding"]
    )

    retriever = qdrant.as_retriever(
        search_type=config["search_type"],
        search_kwargs={
            'k': config["k"],
            "fetch_k": config["fetch_k"],
            "lambda_mult": config["lambda_mult"],
            "filter": None
        }
    )

    return retriever