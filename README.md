>>This is a Flask-based web application that allows users to:

Upload images (PNG, JPG, JPEG, GIF)

Upload documents (PDF, DOCX)

Ask questions about the uploaded file (image or document)

Chat normally if no file is uploaded

Behind the scenes, it uses Google's Gemini 1.5 Flash model (a powerful AI model) to analyze uploaded content and generate responses based on user queries.

>> How it Works (Flow)
User opens the web page (served by Flask).

User uploads either an image or a document via a form.

Images are saved to a folder (uploaded_files/).

Documents (PDF or DOCX) are also saved there.

If the user asks a question:

If an image was uploaded → it sends both the question and image to Gemini for response.

If a document was uploaded → it first extracts text (using PyPDF2 for PDFs and python-docx for DOCX), then sends the question and text to Gemini.

If no file is uploaded → it sends only the question to Gemini.

Gemini model analyzes and generates a smart text response.

Response is shown on the webpage.

>> Technologies Used

Technology	Purpose
Python	Main programming language
Flask	Web framework for building the server
Flask-CORS	Allowing cross-origin requests (important for frontend)
PIL (Pillow)	Image opening and handling
PyPDF2	Reading and extracting text from PDF files
python-docx	Reading and extracting text from DOCX files
google.generativeai	Accessing Gemini AI model
dotenv	Securely load environment variables (API keys etc.)
HTML (index.html)	Simple frontend form for uploads and chatting
