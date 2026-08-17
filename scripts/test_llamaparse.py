import os
from pathlib import Path

from dotenv import load_dotenv
from llama_cloud_services import LlamaParse


PROJECT_ROOT = Path(__file__).resolve().parents[1]

load_dotenv(PROJECT_ROOT / ".env", override=True)

api_key = os.getenv("LLAMA_CLOUD_API_KEY")

if not api_key:
    raise RuntimeError(
        "LLAMA_CLOUD_API_KEY was not found."
    )

print("API key loaded successfully.")
print(f"Key length: {len(api_key)}")
print(f"Key prefix: {api_key[:8]}")

parser = LlamaParse(
    api_key=api_key,
    result_type="markdown",
    language="en",
)

pdf = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "TS_23.501_V17.6.0.pdf"
)

print(f"Testing: {pdf}")

documents = parser.load_data(str(pdf))

if not documents:
    raise RuntimeError(
        "LlamaParse returned zero documents."
    )

print(
    f"SUCCESS: parsed {len(documents)} document(s)"
)