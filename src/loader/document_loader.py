import os
import docx2txt
from PyPDF2 import PdfReader
from tqdm import tqdm

def load_documents(data_dir, max_file_size_mb=50, max_pages=200):
    if not os.path.exists(data_dir):
        print(f"Warning: Directory {data_dir} does not exist. Creating it...")
        os.makedirs(data_dir, exist_ok=True)
        print(f"Please add documents to {data_dir} and run again.")
        return []
    
    print(f"Loading documents from {data_dir}")
    docs = []
    all_files = [f for f in os.listdir(data_dir) 
                 if f.endswith(('.pdf', '.docx', '.txt')) and not f.startswith('.')]
    
    # Filter by file size
    supported_files = []
    for f in all_files:
        file_path = os.path.join(data_dir, f)
        file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
        if file_size_mb > max_file_size_mb:
            print(f"⚠️  Skipping {f} (${file_size_mb:.1f}MB > ${max_file_size_mb}MB limit)")
        else:
            supported_files.append(f)
            print(f"📄 Found: {f} ({file_size_mb:.1f}MB)")
    
    if not supported_files:
        print(f"No supported documents found in {data_dir}")
        print("Supported formats: PDF (.pdf), Word (.docx), Text (.txt)")
        print(f"Files must be under {max_file_size_mb}MB")
        return []
    
    for file_name in tqdm(supported_files, desc="Loading files"):
        path = os.path.join(data_dir, file_name)
        text = ""
        
        try:
            if file_name.endswith(".pdf"):
                reader = PdfReader(path)
                total_pages = len(reader.pages)
                
                # Limit pages for large PDFs to avoid hanging
                # max_pages parameter controls how many pages to process
                pages_to_process = min(total_pages, max_pages)
                
                print(f"  📖 Processing {pages_to_process}/{total_pages} pages...")
                
                text_parts = []
                for i in tqdm(range(pages_to_process), desc=f"  Extracting {file_name}", leave=False):
                    page_text = reader.pages[i].extract_text() or ""
                    text_parts.append(page_text)
                
                text = " ".join(text_parts)
                
                if total_pages > max_pages:
                    print(f"  ⚠️  Only processed first {max_pages} pages (of {total_pages})")
                    
            elif file_name.endswith(".docx"):
                print(f"  📄 Processing Word document...")
                text = docx2txt.process(path)
            elif file_name.endswith(".txt"):
                print(f"  📝 Processing text file...")
                with open(path, 'r', encoding='utf-8') as f:
                    text = f.read()
                
            if not text.strip():
                print(f"Warning: No text extracted from {file_name}")
                continue
                
            chunks = chunk_text(text, chunk_size=1000)
            if chunks:
                docs.append({"file": file_name, "chunks": chunks})
                
        except Exception as e:
            print(f"Error processing {file_name}: {e}")
            continue
            
    return docs

def chunk_text(text, chunk_size=1000, overlap=200):
    """
    Improved chunking with overlapping windows and better boundary detection.
    Larger chunks reduce API calls while overlap maintains context.
    """
    if not text.strip():
        return []
    
    # Clean and normalize text
    text = " ".join(text.split())  # Remove extra whitespace
    
    # If text is smaller than chunk size, return as single chunk
    if len(text) <= chunk_size:
        return [text]
    
    chunks = []
    start = 0
    
    while start < len(text):
        # Define chunk end
        end = start + chunk_size
        
        # If this is not the last chunk, try to find a good breaking point
        if end < len(text):
            # Look for sentence endings near the chunk boundary
            for i in range(min(100, chunk_size // 4)):  # Search within reasonable range
                if end - i > start and text[end - i:end - i + 1] in '.!?':
                    end = end - i + 1
                    break
        
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        
        # Move start position with overlap
        start = max(start + 1, end - overlap)
        
        # Prevent infinite loops
        if start >= len(text):
            break
    
    return chunks
