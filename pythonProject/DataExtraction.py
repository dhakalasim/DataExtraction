import fitz  # PyMuPDF for extracting text
import google.generativeai as genai
import os
import json
from pymongo import MongoClient
from dotenv import load_dotenv  # Import dotenv

# Load environment variables from .env file
load_dotenv()

# Get API key from environment variables
api_key = os.getenv("GEMINI_API_KEY")

# Configure Gemini API
if not api_key:
    raise ValueError("API key is missing! Ensure GEMINI_API_KEY is set in the .env file.")

genai.configure(api_key=api_key)


def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF file."""
    doc = fitz.open(pdf_path)
    extracted_text = "\n".join([page.get_text("text") for page in doc])
    return extracted_text


def analyze_text_with_gemini(text):
    """Send extracted text to Gemini API and get structured JSON data."""
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(
        f"Extract structured data from the following text and return only a valid JSON object. "
        f"Ensure the response is strictly JSON with no additional text, explanations, or markdown formatting. "
        f"If no structured data is found, return an empty JSON object: {{}}\n\n{text}"
    )

    raw_text = response.text.strip()

    # Remove Markdown formatting (e.g., ```json ... ```)
    if raw_text.startswith("```json"):
        raw_text = raw_text[7:]  # Remove the first 7 characters (```json)
    if raw_text.endswith("```"):
        raw_text = raw_text[:-3]  # Remove the last 3 characters (```)

    raw_text = raw_text.strip()  # Clean extra spaces or new lines

    # Debugging: Print cleaned response
    print("\nCleaned JSON Response:\n", raw_text)

    try:
        # Ensure it's valid JSON
        json_data = json.loads(raw_text)
        return json.dumps(json_data, indent=4)  # Pretty-print JSON
    except json.JSONDecodeError:
        print("❌ Error: Gemini AI returned an invalid JSON response.")
        return "{}"  # Return an empty JSON object if parsing fails



def save_json_file(output_path, json_text):
    """Save structured JSON response to a .json file."""
    if json_text.strip() == "{}":  # Check if JSON is empty
        print("⚠️ Warning: No structured data to save.")
        return

    try:
        with open(output_path, "w", encoding="utf-8") as json_file:
            json_file.write(json_text)
            json_file.flush()
        print(f"✅ JSON response saved successfully to {output_path}")
    except Exception as e:
        print(f"❌ Error saving response to JSON file: {e}")


def insert_json_to_mongodb(json_file_path, db_name="pdf_data", collection_name="extracted_text"):
    """Insert JSON data into MongoDB."""
    try:
        # Connect to MongoDB
        client = MongoClient("mongodb://localhost:27017/")
        db = client[db_name]
        collection = db[collection_name]

        # Load JSON data from file
        with open(json_file_path, "r", encoding="utf-8") as file:
            json_data = json.load(file)

        # Ensure valid JSON structure
        if not json_data or not isinstance(json_data, dict):
            print("⚠️ Warning: JSON data is empty or invalid. Skipping insertion.")
            return

        collection.insert_one(json_data)
        print(f"✅ Successfully inserted JSON data into MongoDB collection '{collection_name}' in database '{db_name}'.")

    except json.JSONDecodeError:
        print("❌ Error: The JSON file is corrupted or invalid.")
    except Exception as e:
        print(f"❌ MongoDB Insertion Error: {e}")


if __name__ == "__main__":
    pdf_path = "/Users/asimdhakal/PycharmProjects/pythonProject/MasonCV.pdf"

    # Step 1: Extract text from PDF
    extracted_text = extract_text_from_pdf(pdf_path)
    print("Extracted Text:\n", extracted_text)

    # Step 2: Get structured JSON response from Gemini AI
    raw_response = analyze_text_with_gemini(extracted_text)
    print("\nRaw API Response:\n", raw_response)

    # Step 3: Save the JSON response to a file
    output_json_path = "/Users/asimdhakal/PycharmProjects/pythonProject/raw_api_response.json"
    save_json_file(output_json_path, raw_response)

    # Step 4: Insert the JSON data into MongoDB
    insert_json_to_mongodb(output_json_path)
