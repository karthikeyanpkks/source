from fastapi import FastAPI, File, UploadFile
import spacy
import pytesseract
from pdf2image import convert_from_path
import shutil
import os
import openai  # Ensure `openai` is installed (`pip install openai`)

# Load OpenAI API key from environment variable
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OpenAI API key is missing! Set it as an environment variable.")

# Initialize OpenAI client
client = openai.OpenAI(api_key=OPENAI_API_KEY)

app = FastAPI()

# Load NLP model with error handling
try:
    nlp = spacy.load("./invoice_ner_model/model/model-last")
except Exception as e:
    print(f"Error loading NLP model: {e}")
    nlp = None  # Set to None if model fails to load


@app.get("/")
def read_root():
    """Root endpoint to check API status."""
    return {"message": "API is working!"}


@app.post("/extract")
async def extract_entities(text: str):
    """Extract entities from text using the NLP model."""
    if nlp is None:
        return {"error": "NLP model not loaded. Please check the model path."}

    doc = nlp(text)
    entities = {ent.label_: ent.text for ent in doc.ents}
    return {"extracted_data": entities}


@app.post("/ocr")
async def ocr(file: UploadFile = File(...)):
    """Perform OCR on a PDF and return extracted text."""
    try:
        # Save uploaded file temporarily
        temp_file_path = f"./temp_{file.filename}"
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Convert PDF pages to images
        images = convert_from_path(temp_file_path)

        # Perform OCR on each page
        extracted_text = [pytesseract.image_to_string(image) for image in images]

        # Remove temporary file
        os.remove(temp_file_path)

        return {"extracted_text": "\n".join(extracted_text)}

    except Exception as e:
        return {"error": str(e)}


@app.post("/process")
async def process_pdf(file: UploadFile = File(...)):
    """
    Upload a PDF, extract text using OCR, process it with NLP,
    and return the structured invoice data.
    """
    try:
        # Save uploaded file temporarily
        temp_file_path = f"./temp_{file.filename}"
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Convert PDF pages to images
        images = convert_from_path(temp_file_path)

        # Perform OCR on each page
        extracted_text = [pytesseract.image_to_string(image) for image in images]
        full_text = "\n".join(extracted_text)

        # Remove temporary file
        os.remove(temp_file_path)

        # NLP Processing
        if nlp is None:
            return {"extracted_text": full_text, "error": "NLP model not loaded."}

        doc = nlp(full_text)
        entities = {ent.label_: ent.text for ent in doc.ents}

        return {"extracted_text": full_text, "structured_data": entities}

    except Exception as e:
        return {"error": str(e)}


@app.post("/process2")
async def process_pdfv2(file: UploadFile = File(...)):
    """
    Upload a PDF, extract text using OCR, process it with OpenAI,
    and return the AI-processed structured invoice data.
    """
    try:
        # Save uploaded file temporarily
        temp_file_path = f"./temp_{file.filename}"
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Convert PDF pages to images
        images = convert_from_path(temp_file_path)

        # Perform OCR on each page
        extracted_text = [pytesseract.image_to_string(image) for image in images]
        full_text = "\n".join(extracted_text)

        # Remove temporary file
        os.remove(temp_file_path)

        # OpenAI Processing
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": f"Extract structured data from this invoice:\n{full_text}"}],
        )

        return {"extracted_text": full_text, "ai_structured_data": completion.choices[0].message.content}

    except Exception as e:
        return {"error": str(e)}
