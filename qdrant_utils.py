from langchain_qdrant import Qdrant
from qdrant_client import QdrantClient
from langchain_huggingface import HuggingFaceEmbeddings
# from langchain.embeddings import HuggingFaceEmbeddings


import os
os.environ["QDRANT_URL"] = "https://74a1497a-d878-447a-a1e2-bd533d622803.europe-west3-0.gcp.cloud.qdrant.io"  # Replace with your Qdrant URL
os.environ["QDRANT_API_KEY"] = "8chBjqw80ySjOo857zhWm5NHFGhEnYSprJOC6z1vXnYP6kyXkqRpqg"  # Replace with your actual Qdrant API key
def get_secret(secret_name):
    """Retrieve the secret from environment variables."""
    secret = os.getenv(secret_name)
    if secret is None:
        raise ValueError(f"Secret {secret_name} not found in environment variables.")
    return secret


# Initialize Qdrant client and retriever
def get_retriever():
    # Get Qdrant credentials from Hugging Face environment variables
    qdrant_url = get_secret("QDRANT_URL")
    qdrant_api_key = get_secret("QDRANT_API_KEY")

    # Initialize embedding model (HuggingFace MiniLM)
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    # Set up Qdrant client
    qdrant_client = QdrantClient(url=qdrant_url, api_key=qdrant_api_key)
    qdrant = Qdrant(
        client=qdrant_client,
        collection_name="Legal Guide PK-app",  # Your existing collection name
        embeddings=embeddings                  # Use the same embedding model
    )
    
    # Return the retriever for document search
    return qdrant.as_retriever(search_kwargs={"k": 5})
