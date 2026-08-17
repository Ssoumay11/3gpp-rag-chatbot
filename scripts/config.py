import os

from dotenv import load_dotenv

load_dotenv()


# --------------------------------------------------
# API
# --------------------------------------------------

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
LLAMA_CLOUD_API_KEY = os.getenv("LLAMA_CLOUD_API_KEY")


# --------------------------------------------------
# Qdrant
# --------------------------------------------------

QDRANT_URL = os.getenv(
    "QDRANT_URL",
    "http://localhost:6333",
)

QDRANT_GRPC_URL = os.getenv(
    "QDRANT_GRPC_URL",
    "localhost:6334",
)

QDRANT_COLLECTION = os.getenv(
    "QDRANT_COLLECTION",
    "3gpp_documents",
)


# --------------------------------------------------
# Embeddings
# --------------------------------------------------

EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL",
    "BAAI/bge-small-en-v1.5",
)


# --------------------------------------------------
# Documents
# --------------------------------------------------

RAW_DATA_DIR = "data/raw"
PARSED_DATA_DIR = "data/parsed"
MANIFEST_DIR = "data/manifests"