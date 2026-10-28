import os
import sys

from dotenv import load_dotenv
from google import genai

MODEL = "gemma-4-26b-a4b-it"

load_dotenv()
if not os.environ.get("GEMINI_API_KEY"):
    sys.exit(
        "GEMINI_API_KEY is not set. Copy .env.example to .env and paste "
        "your key from https://aistudio.google.com"
    )

client = genai.Client()
response = client.models.generate_content(
    model=MODEL,
    contents="Reply with one short sentence confirming you are working.",
)
print(f"{MODEL}: {response.text}")
