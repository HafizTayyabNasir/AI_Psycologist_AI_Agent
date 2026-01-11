import os
import traceback
from dotenv import load_dotenv
import google.generativeai as genai

print("--- Starting Standalone Image Generation Test ---")

try:
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in .env file.")

    print("✅ API Key Loaded. Configuring GenAI...")
    genai.configure(api_key=api_key)

    print("✅ GenAI Configured. Initializing 'imagen-3' model...")
    image_model = genai.GenerativeModel("imagen-3")
    print("✅ Model Initialized.")

    prompt = "a high-quality photograph of a majestic lion on the savanna"
    print(f"✅ Generating image with prompt: '{prompt}'")

    response = image_model.generate_content(prompt)
    print("✅ Received response from Google API.")

    if response and hasattr(response, 'images') and len(response.images) > 0:
        image_bytes = response.images[0]._image_bytes
        with open("output_image.png", "wb") as f:
            f.write(image_bytes)
        print("\n🎉 SUCCESS! Image was generated and saved as 'output_image.png' in your project folder.")
    else:
        print("\n🔴 FAILURE: The API response did not contain an image.")

except Exception as e:
    print("\n\n🔴🔴🔴 AN ERROR OCCURRED! 🔴🔴🔴")
    print(f"Error Type: {type(e).__name__}")
    print(f"Error Details: {e}")
    print("--- FULL TRACEBACK ---")
    traceback.print_exc()
    print("----------------------")

print("--- Test Finished ---")