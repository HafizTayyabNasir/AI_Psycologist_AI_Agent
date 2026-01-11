import os
import google.generativeai as genai
from dotenv import load_dotenv

print("--- Checking for IMAGE GENERATION Models ---")

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("🔴 ERROR: GEMINI_API_KEY not found.")
else:
    try:
        genai.configure(api_key=api_key)
        print("✅ API key configured. Fetching list...\n")

        print("--- Image Generation Models Available to You ---")
        found_one = False
        for m in genai.list_models():
            if "generateImage" in m.supported_generation_methods:
                print(f"✅ {m.name}")
                found_one = True

        if not found_one:
            print(
                "\n🔴 No direct image generation models found. Checking for vision models with generation capabilities..."
            )
            for m in genai.list_models():
                if (
                    "generateContent" in m.supported_generation_methods
                    and "vision" in m.name
                ):
                    print(f"❔ Possible candidate: {m.name}")

        print("---------------------------------------------")

    except Exception as e:
        print(f"🔴 An error occurred: {e}")