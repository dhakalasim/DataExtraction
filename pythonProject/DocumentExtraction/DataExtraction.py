import fitz  # PyMuPDF for extracting text
import google.generativeai as genai
import os
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
    """Send extracted text to Gemini API and get structured data in JSON format."""
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(
        f"Extract relevant structured data from the following text and return a valid JSON object. "
        f"Ensure the response is properly formatted as JSON and does not contain any additional text. "
        f"If no relevant data is found, return an empty JSON object: {{}}\n\n{text}"
    )

    # Debug: Print raw API response
    print("Raw API Response:", response.text)

    # Return raw API response text (not parsed into structured JSON)
    return response.text


def save_json_file(output_path, json_text):
    """Save raw API response to a .json file."""
    if not json_text.strip():  # Ensure response is not empty
        print("Error: No data to save")
        return

    try:
        # Save the raw response (without formatting it as structured JSON)
        with open(output_path, "w", encoding="utf-8") as json_file:
            json_file.write(json_text)
            json_file.flush()  # Ensure data is written before closing
        print(f"✅ Raw response saved successfully to {output_path}")
    except Exception as e:
        print(f"❌ Error saving response to JSON file: {e}")


if __name__ == "__main__":
    pdf_path = "/Users/asimdhakal/PycharmProjects/pythonProject/AsimResume.pdf"
    extracted_text = extract_text_from_pdf(pdf_path)

    print("Extracted Text:\n", extracted_text)

    # Get raw API response
    raw_response = analyze_text_with_gemini(extracted_text)
    print("\nRaw API Response:\n", raw_response)

    # Save raw API response to a .json file
    output_json_path = "/Users/asimdhakal/PycharmProjects/pythonProject/raw_api_response.json"
    save_json_file(output_json_path, raw_response)

    print(f"\nRaw API response has been saved to {output_json_path}")