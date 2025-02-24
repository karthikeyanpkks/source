import pytesseract 
from pdf2image import convert_from_path

# Convert PDF to images
images = convert_from_path("invoice.pdf")

# Perform OCR
for i, image in enumerate(images):
    text = pytesseract.image_to_string(image)
    print(f"Page {i+1} OCR Output:\n", text)