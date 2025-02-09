from flask import Flask, render_template, request, jsonify
import pytesseract
from PIL import Image
import requests
import io
import base64

app = Flask(__name__)

# Set the path to the Tesseract executable (update this path as per your system)
pytesseract.pytesseract.tesseract_cmd = r"C:\Users\ADITYA TIWARI\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"

# Replace with your Mistral AI API key
MISTRAL_API_KEY = "bNgsRHmJakgoQsJpk59ymxoLO8XqjLRD"
MISTRAL_API_URL = "https://api.mistral.ai/v1/chat/completions"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process_image', methods=['POST'])
def process_image():
    data = request.json
    if not data or 'image' not in data:
        return jsonify({"error": "No image data provided"}), 400

    try:
        # Decode the base64 image
        image_data = base64.b64decode(data['image'].split(',')[1])
        image = Image.open(io.BytesIO(image_data))

        # Extract text using OCR
        extracted_text = pytesseract.image_to_string(image).strip()

        if not extracted_text:
            return jsonify({"error": "No text extracted from image"}), 400

        # Clean up the extracted text (basic cleanup)
        extracted_text = extracted_text.replace("\n", " ").replace("\r", "")
        extracted_text = ' '.join(extracted_text.split())  # Remove extra spaces

        if not extracted_text:
            return jsonify({"error": "No meaningful text extracted"}), 400

        # Log extracted text to debug
        print("Extracted Text:", extracted_text)

        # Query the Mistral AI API
        headers = {
            "Authorization": f"Bearer {MISTRAL_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "mistral-small-latest",
            "temperature": 0.3,  # Reduce temperature for more deterministic responses
            "top_p": 1,
            "max_tokens": 150,  # Limit the response length
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": extracted_text}
            ],
            "response_format": {"type": "text"}
        }
        response = requests.post(MISTRAL_API_URL, json=payload, headers=headers)

        if response.status_code == 200:
            answer = response.json().get("choices", [{}])[0].get("message", {}).get("content", "No answer found")
            return jsonify({"extracted_text": extracted_text, "answer": answer})
        else:
            return jsonify({"error": "Failed to query Mistral API", "details": response.text}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
