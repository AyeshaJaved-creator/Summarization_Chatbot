from flask import Flask, render_template, request
from PyPDF2 import PdfReader
import requests
from bs4 import BeautifulSoup
from transformers import pipeline

# Initialize the summarization pipeline with a specified model to avoid warnings
summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")

app = Flask(__name__)

# Function to extract text from PDF files
def extract_text_from_pdf(pdf_file):
    reader = PdfReader(pdf_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text

# Function to extract text from web pages
def extract_text_from_url(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    return ' '.join([p.get_text() for p in soup.find_all('p')])

# Function to summarize text
def summarize_text(text, max_length=150):
    if len(text.split()) > max_length:
        return summarizer(text, max_length=max_length, min_length=50, do_sample=False)[0]['summary_text']
    else:
        return "The text is too short for summarization."

# Flask Routes
@app.route('/', methods=['GET', 'POST'])
def index():
    summary = None
    extracted_text = None

    if request.method == 'POST':
        # Handle PDF or text file upload
        uploaded_file = request.files.get('file')
        url = request.form.get('url')

        if uploaded_file:
            if uploaded_file.filename.endswith(".pdf"):
                extracted_text = extract_text_from_pdf(uploaded_file)
            elif uploaded_file.filename.endswith(".txt"):
                extracted_text = uploaded_file.read().decode("utf-8")
            else:
                extracted_text = "Unsupported file type."

        elif url:
            try:
                extracted_text = extract_text_from_url(url)
            except Exception as e:
                extracted_text = f"Failed to extract text from the URL: {e}"

        if extracted_text:
            summary = summarize_text(extracted_text)

    return render_template('index.html', summary=summary, extracted_text=extracted_text)

if __name__ == "__main__":
    app.run(debug=True)
