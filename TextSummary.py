from flask import Flask, request, jsonify
from PyPDF2 import PdfReader
from transformers import pipeline
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

# Initialize the summarization pipeline
summarizer = pipeline("summarization")

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

@app.route('/summarize', methods=['POST'])
def summarize():
    content = request.json
    text = content.get("text")
    max_length = content.get("max_length", 150)
    min_length = content.get("min_length", 50)

    if not text:
        return jsonify({"error": "No text provided"}), 400

    if len(text.split()) > max_length:
        summary = summarizer(text, max_length=max_length, min_length=min_length, do_sample=False)[0]['summary_text']
        return jsonify({"summary": summary})
    else:
        return jsonify({"error": "Text too short for summarization"}), 400

@app.route('/extract-pdf', methods=['POST'])
def extract_pdf():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    text = extract_text_from_pdf(file)
    return jsonify({"text": text})

@app.route('/extract-url', methods=['POST'])
def extract_url():
    url = request.json.get("url")
    if not url:
        return jsonify({"error": "No URL provided"}), 400

    try:
        text = extract_text_from_url(url)
        return jsonify({"text": text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
