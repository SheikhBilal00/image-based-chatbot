import os
import PIL.Image
import google.generativeai as genai
from dotenv import load_dotenv
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from PyPDF2 import PdfReader
from docx import Document

# Load environment variables
load_dotenv()
genai.configure(api_key=os.getenv('gemini_api'))
model = genai.GenerativeModel(model_name="gemini-1.5-flash")

app = Flask(__name__)
CORS(app)

app.config['UPLOAD_FOLDER'] = 'uploaded_files'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'docx'}

current_image_path = None
current_file_path = None
current_file_type = None

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/api/upload_image', methods=['POST'])
def upload_image():
    global current_image_path, current_file_path, current_file_type
    file = request.files.get('file')
    if not file or file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type'}), 400

    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(file_path)
    current_image_path = file_path
    current_file_path = None
    current_file_type = 'image'

    return jsonify({'message': 'Image uploaded successfully.'})

@app.route('/api/upload_document', methods=['POST'])
def upload_document():
    global current_file_path, current_image_path, current_file_type
    file = request.files.get('file')
    if not file or file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type'}), 400

    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(file_path)
    current_file_path = file_path
    current_image_path = None
    current_file_type = 'document'

    return jsonify({'message': 'Document uploaded successfully.'})

@app.route('/api/chat', methods=['POST'])
def chat():
    global current_image_path, current_file_path, current_file_type
    data = request.get_json()
    user_message = data.get('message', '')
    file_question = data.get('fileQuestion', '')

    if current_file_type == 'image' and current_image_path:
        bot_response = handle_message(user_message, current_image_path)
    elif current_file_type == 'document' and current_file_path:
        bot_response = handle_message(user_message, current_file_path)
    else:
        bot_response = generate_response(user_message, file_question)

    return jsonify({'response': bot_response})

def generate_response(message, content):
    if message or content:
        response = model.generate_content([message, content], generation_config=genai.GenerationConfig(temperature=0.5))
        return response.text
    return 'Please ask a question or upload a file.'

def handle_message(message, file_path):
    try:
        file_extension = file_path.rsplit('.', 1)[1].lower()

        if file_extension in {'png', 'jpg', 'jpeg', 'gif'}:
            image = PIL.Image.open(file_path)
            response = model.generate_content([message, image])
        elif file_extension == 'pdf':
            text = extract_text_from_pdf(file_path)
            response = model.generate_content([message, text])
        elif file_extension == 'docx':
            text = extract_text_from_docx(file_path)
            response = model.generate_content([message, text])
        else:
            return 'Unsupported file type.'

        return response.text
    except Exception as e:
        print(f"Error handling message: {e}")
        return 'Error processing the file.'

def extract_text_from_pdf(file_path):
    try:
        text = ''
        with open(file_path, 'rb') as file:
            reader = PdfReader(file)
            for page in reader.pages:
                text += page.extract_text() or ''
        return text
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return 'Error extracting text from PDF.'

def extract_text_from_docx(file_path):
    try:
        text = ''
        doc = Document(file_path)
        for para in doc.paragraphs:
            text += para.text + '\n'
        return text
    except Exception as e:
        print(f"Error extracting text from DOCX: {e}")
        return 'Error extracting text from DOCX.'

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
