import os

from dotenv import load_dotenv


load_dotenv(override=True)


key = os.getenv("GROQ_API_KEY")


print("=" * 60)
print("Groq API Key Check")
print("=" * 60)

if not key:
    print("GROQ_API_KEY: NOT FOUND")

elif key == "your_groq_api_key_here":
    print("GROQ_API_KEY: PLACEHOLDER VALUE")

else:
    print("GROQ_API_KEY: FOUND")
    print(f"Length: {len(key)}")
    print(f"Prefix: {key[:7]}...")