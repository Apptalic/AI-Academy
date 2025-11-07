import requests
from bs4 import BeautifulSoup
from PyPDF2 import PdfReader

def process_file(uploaded_file):
  """
  Processes an uploaded file (PDF or TXT) and extracts its content.
  Args:
      uploaded_file: The uploaded file object from Streamlit.
  Returns:
      str: Extracted text content from the file.
  """
  try:
    if uploaded_file.type == "application/pdf":
      pdf_reader = PdfReader(uploaded_file)
      text = ""
      for page in pdf_reader.pages:
        text += page.extract_text()
    elif uploaded_file.type == "text/plain":
      text = uploaded_file.read().decode("utf-8")
    else:
      raise ValueError("This file is not supported. Upload a PDF or TXT file.")
    
    return text 
  except Exception as e:
    raise RuntimeError(f"Error processing file: {str(e)}")
  

def process_url(url):
  """
  Fetches and processes content from a public URL.
  Args:
      url: The URL of the blog post.
  Returns:
      str: Extracted text content from the URL.
  """
  try:
    response = requests.get(url) 
    response.raise_for_status()  # Raise an error for HTTP issues 

    page_content = BeautifulSoup(response.text, "html.parser")

    # Extract headings and paragraphs
    content = []
    for tag in page_content.find_all(["h1", "h2", "h3", "p"]):
      content.append(tag.get_text(strip=True))

    text = "\n\n".join(content)

    if not text.strip():
      raise ValueError("No readable content found at this provided URL")
    
    return text

  except Exception as e:
    raise RuntimeError(f"Error processing URL: {str(e)}") 


