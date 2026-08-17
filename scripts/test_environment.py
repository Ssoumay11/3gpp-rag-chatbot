import os
import sys

try:
    import qdrant_client
except Exception:
    qdrant_client = None

try:
    import streamlit
except Exception:
    streamlit = None

try:
    import llama_index.core
except Exception:
    llama_index = None

from dotenv import load_dotenv

load_dotenv()


def check_env_variable(name: str) -> None:
    value = os.getenv(name)

    if value:
        print(f"{name}: configured")
    else:
        print(f"{name}: NOT configured")


def main() -> None:
    print("=" * 60)
    print("3GPP RAG - Environment Test")
    print("=" * 60)

    print(f"\nPython: {sys.version.split()[0]}")
    # qdrant_client may be missing or may not expose a __version__ attribute
    if qdrant_client is None:
        print("Qdrant client: not installed")
    else:
        qdrant_version = getattr(qdrant_client, "__version__", None)
        if not qdrant_version:
            try:
                from importlib import metadata

                # try common distribution names
                for name in ("qdrant-client", "qdrant_client", "qdrant"):
                    try:
                        qdrant_version = metadata.version(name)
                        break
                    except metadata.PackageNotFoundError:
                        continue
            except Exception:
                qdrant_version = None

        print(f"Qdrant client: {qdrant_version or 'unknown'}")
    if streamlit is None:
        print("Streamlit: not installed")
    else:
        print(f"Streamlit: {getattr(streamlit, '__version__', 'unknown')}")

    if llama_index is None:
        print("LlamaIndex Core: not installed")
    else:
        # llama_index.core may or may not expose __version__
        core_version = getattr(getattr(llama_index, 'core', None), '__version__', None)
        print(f"LlamaIndex Core: {core_version or 'unknown'}")

    print("\nEnvironment variables:")

    check_env_variable("GROQ_API_KEY")
    check_env_variable("LLAMA_CLOUD_API_KEY")

    print("\nEnvironment check complete.")


if __name__ == "__main__":
    main()