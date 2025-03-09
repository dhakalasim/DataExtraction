from flask import Flask, jsonify, send_file, send_from_directory
from flask_cors import CORS
import json
import os

app = Flask(__name__)
CORS(app)  # Allow frontend requests

# Paths
JSON_FILE_PATH = "/Users/asimdhakal/PycharmProjects/pythonProject/raw_api_response.json"
PDF_PATH = "/Users/asimdhakal/PycharmProjects/pythonProject/MasonCV.pdf"

@app.route('/get-extracted-data', methods=['GET'])
def get_extracted_data():
    try:
        with open(JSON_FILE_PATH, "r", encoding="utf-8") as file:
            json_data = json.load(file)

        # Construct the PDF URL for the frontend
        json_data["pdf_url"] = "http://127.0.0.1:5000/get-pdf"

        return jsonify(json_data)
    except Exception as e:
        return jsonify({"error": str(e)})

# Route to serve the PDF file
@app.route('/get-pdf', methods=['GET'])
def get_pdf():
    return send_file(PDF_PATH, mimetype='application/pdf', as_attachment=False)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
