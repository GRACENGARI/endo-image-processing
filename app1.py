import os
from flask import Flask, render_template, request
from PIL import Image
import io
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Configure Google Gemini API
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-1.5-flash')

@app.route('/', methods=['GET'])
def index():
    return render_template('steps.html')  # Assuming steps.html provides instructions

@app.route('/analyze', methods=['POST'])
def analyze():
    if 'file' not in request.files:
        return render_template('error.html', message="No file uploaded")  # Error handling with a template

    file = request.files['file']
    if file.filename == '':
        return render_template('error.html', message="No file selected")

    if not file or not allowed_file(file):
        return render_template('error.html', message="Invalid file type")

    # A valid image is uploaded, so now let's process it
    image_data = Image.open(file.stream)
    analysis = analyze_image(image_data)

    return render_template('results.html', analysis=analysis)  # Pass analysis data to a results template

def analyze_image(image):
    prompt = ("Analyze the attached ultrasound image to identify potential indicators or markers "
              "of endometriosis. Focus on identifying any abnormal tissue formations, cysts, or "
              "signs of inflammation in the uterine or pelvic region. Provide a high-level summary "
              "that a non-medical person could understand, and offer an interpretation that suggests "
              "whether further clinical assessment may be needed.")

    response = model.generate_content([prompt, image])

    # Extract findings, summary, and recommendation from the response (assuming specific format)
    findings = response.find("findings:")[len("findings: "):]
    summary = response.find("summary:")[len("summary: "):]
    recommendation = response.find("recommendation:")[len("recommendation: "):]

    return {
        "findings": findings,
        "summary": summary,
        "recommendation": recommendation
    }

def allowed_file(file_object):
    # Check if the filename has an extension in the allowed list and is a valid image
    filename = file_object.filename
    if not '.' in filename or filename.rsplit('.', 1)[1].lower() not in {'png', 'jpg', 'jpeg', 'gif'}:
        return False

    try:
        # Attempt to open and verify the image
        img = Image.open(file_object.stream)
        img.verify()  # Verify that it's a valid image file
        file_object.stream.seek(0)  # Reset file pointer
        return True
    except Exception as e:
        # If any exception occurs during image verification, consider the file invalid
        return False

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))