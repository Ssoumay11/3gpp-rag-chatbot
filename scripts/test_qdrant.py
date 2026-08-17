import os
import sys

from dotenv import load_dotenv
from qdrant_client import QdrantClient

load_dotenv()

QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")


def main() -> None:
    print("=" * 60)
    print("3GPP RAG - Qdrant Connection Test")
    print("=" * 60)

    print(f"Qdrant URL: {QDRANT_URL}")

    try:
        client = QdrantClient(url=QDRANT_URL)

        collections = client.get_collections()

        print("\nConnection: SUCCESS")
        print(f"Existing collections: {len(collections.collections)}")

        if collections.collections:
            print("\nCollections:")
            for collection in collections.collections:
                print(f"  - {collection.name}")
        else:
            print("  No collections yet.")

        print("\nQdrant is ready.")

    except Exception as exc:
        print("\nConnection: FAILED")
        print(f"Error: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()