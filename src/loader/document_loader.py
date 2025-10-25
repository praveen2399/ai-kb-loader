import os
import docx2txt
from PyPDF2 import PdfReader

def load_documents(data_dir):
    docs = []
    for file_name in os.listdir(data_dir):
        path = os.path.join(data_dir, file_name)
        if file_name.endswith(".pdf"):
            reader = PdfReader(path)
            text = " ".join([page.extract_text() or "" for page in reader.pages])
        elif file_name.endswith(".docx"):
            text = docx2txt.process(path)
        else:
            continue

        chunks = chunk_text(text, size=500)
        docs.append({"file": file_name, "chunks": chunks})
    return docs

def chunk_text(text, size=500):
    words = text.split()
    return [" ".join(words[i:i+size]) for i in range(0, len(words), size)]
