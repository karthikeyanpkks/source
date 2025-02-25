import spacy
from spacy.tokens import DocBin

TRAIN_DATA = [
    ("Invoice No # ANT23241219 Invoice Date Jan 31, 2025 Due Date Feb 15, 2025",
     {"entities": [(12, 23, "INVOICE_NO"), (35, 46, "INVOICE_DATE"), (57, 68, "DUE_DATE")]}),

    ("Billed By Antbuild Software Pvt Ltd Billed To DRSLINX Logistics Worldwide Pvt Ltd",
     {"entities": [(10, 39, "BILLED_BY"), (50, 90, "BILLED_TO")]}),

    ("Total (INR) 718,000.00", 
     {"entities": [(12, 21, "TOTAL_AMOUNT")]}),
]

def train_model():
    nlp = spacy.blank("en")  # Create blank English model
    db = DocBin()

    for text, annotations in TRAIN_DATA:
        doc = nlp.make_doc(text)
        ents = []
        for start, end, label in annotations["entities"]:
            span = doc.char_span(start, end, label=label)
            if span is None:
                print(f"Skipping misaligned entity: {text[start:end]}")
                continue
            ents.append(span)
        doc.ents = ents
        db.add(doc)

    db.to_disk("training_data.spacy")
    print("Training data saved.")

train_model()
