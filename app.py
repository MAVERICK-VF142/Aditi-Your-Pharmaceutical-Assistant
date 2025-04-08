import os
import json
import base64
from flask import Flask, render_template, request
from PIL import Image
from io import BytesIO
import google.generativeai as genai

# Load Gemini API key
api_key = os.getenv("GEMINI_KEY")
genai.configure(api_key=api_key)

# Load Gemini model
model = genai.GenerativeModel("gemini-2.0-flash")

# Initialize Flask app
app = Flask(__name__)

# Function: Get drug info from text
def get_drug_information(drug_name):
    prompt = f"""Provide a clinical summary for pharmacists on the drug {drug_name}.
Include therapeutic uses, standard dosage, common & serious side effects, contraindications, and important drug interactions.
Focus on safe & efficient patient care."""
    response = model.generate_content(prompt)
    return response.text

# Function: Recommend drugs based on symptoms
def symptom_checker(symptoms):
    prompt = f"""Given the symptoms: {symptoms}, recommend over-the-counter treatment options.
Include side effects, interactions, and safety tips for pharmacists. 
Clarify this is educational and not a substitute for diagnosis."""
    response = model.generate_content(prompt)
    return response.text

# Function: Analyze medicine image using Gemini Vision
def analyze_image_with_gemini(image_data):
    try:
        # Decode base64 string to raw image bytes
        image_base64 = image_data.split(',')[1]
        image_bytes = base64.b64decode(image_base64)

        # Convert to PIL Image (what Gemini expects)
        image = Image.open(BytesIO(image_bytes))

        prompt = """Analyze this image of a medicine or drug packaging. 
Identify the drug name, manufacturer (if visible), and give a brief clinical summary.
If the image is blurry or unclear, ask the user to retake it politely."""

        # Use Gemini Vision with image + prompt
        response = model.generate_content([prompt, image])
        return response.text

    except Exception as e:
        return f"❌ Error during image analysis: {str(e)}"

# Routes
@app.route('/')
def sisu():
    return render_template('sisu.html')

@app.route('/index.html')
def index():
    return render_template('index.html')

@app.route('/drug-info-page')
def drug_info_page():
    return render_template('drug_info.html')

@app.route('/symptom-checker-page')
def symptom_checker_page():
    return render_template('symptom_checker.html')

@app.route('/upload-image-page')
def upload_image_page():
    return render_template('upload_image.html')

# AJAX drug info
@app.route('/get_drug_info', methods=['POST'])
def get_drug_info():
    data = request.get_json()
    drug_name = data.get('drug_name')
    response = get_drug_information(drug_name)
    return json.dumps({'response': response})

# AJAX symptom checker
@app.route('/symptom_checker', methods=['POST'])
def symptom_check():
    data = request.get_json()
    symptoms = data.get('symptoms')
    response = symptom_checker(symptoms)
    return json.dumps({'response': response})

# POST route for uploaded image
@app.route('/process-upload', methods=['POST'])
def process_upload():
    image_data = request.form.get("image_data")
    if image_data:
        result = analyze_image_with_gemini(image_data)
        return render_template("upload_image.html", result=result)
    return render_template("upload_image.html", result="❌ No image data received.")

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
