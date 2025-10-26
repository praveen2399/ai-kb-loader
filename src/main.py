import time
import os
import json
from dotenv import load_dotenv
from loader.document_loader import load_documents
import sys
from embeddings.embedder import embed_documents
from vectorstore.faiss_indexer import save_to_faiss

# Load environment variables from .env file
load_dotenv()

def main():
    start_time = time.time()
    
    print("=== AI Knowledge Base Loader ===")
    
    # Check for test mode
    test_mode = len(sys.argv) > 1 and sys.argv[1] == "--test"
    if test_mode:
        print("🧪 Running in TEST MODE (limited processing)")
    
    # Check if we have documents to process
    data_dir = "data/"  # Relative to project root
    if not os.path.exists(data_dir):
        os.makedirs(data_dir, exist_ok=True)
    
    print("Step 1/4: Loading documents...")
    step_start = time.time()
    
    # Limit file size and pages in test mode
    max_size = 5 if test_mode else 50
    max_pages = 10 if test_mode else 1000  # Increased to process more pages
    docs = load_documents(data_dir, max_file_size_mb=max_size, max_pages=max_pages)
    
    if not docs:
        print("\n❌ No documents found!")
        print(f"📁 Please add PDF or DOCX files to: {os.path.abspath(data_dir)}")
        print("📋 Supported formats: .pdf, .docx")
        print("💡 Example: Copy your documents to the data/ folder and run again")
        return
    
    print(f"✓ Loaded {len(docs)} documents ({time.time() - step_start:.2f}s)")

    print("\nStep 2/4: Processing chunks...")
    step_start = time.time()
    
    # Create chunks with metadata
    chunks = []
    metadata = []
    
    for doc in docs:
        for chunk_text in doc['chunks']:
            chunks.append(chunk_text)
            metadata.append({
                'id': f"{doc['file']}_{len(metadata)}",
                'source': doc['file'],
                'page': 0,  # Page info not available from current loader
                'chunk_index': len(metadata),
                'text_length': len(chunk_text),
                'timestamp': time.time()
            })
    
    if not chunks:
        print("❌ No text chunks created from documents")
        return
    
    # Limit chunks in test mode
    if test_mode and len(chunks) > 10:
        print(f"🧪 Test mode: Processing only first 10 chunks (of {len(chunks)})")
        chunks = chunks[:10]
        metadata = metadata[:10]
        
    print(f"✓ Created {len(chunks)} chunks ({time.time() - step_start:.2f}s)")

    print("\nStep 3/4: Generating embeddings...")
    step_start = time.time()
    
    # Check for OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY environment variable not set")
        print("💡 Set it with: export OPENAI_API_KEY='your-api-key-here'")
        return
    
    vectors, ids = embed_documents(chunks)
    print(f"✓ Generated embeddings ({time.time() - step_start:.2f}s)")

    print("\nStep 4/4: Saving FAISS index and metadata...")
    step_start = time.time()
    
    # Save FAISS index
    save_to_faiss(vectors, ids, "vector_db_index.index")
    
    # Save metadata to JSON file
    metadata_file = "metadata.json"
    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump({
            'metadata': metadata,
            'total_chunks': len(chunks),
            'total_documents': len(docs),
            'created_at': time.time(),
            'test_mode': test_mode
        }, f, indent=2, ensure_ascii=False)
    
    print(f"✓ FAISS index and metadata saved ({time.time() - step_start:.2f}s)")
    print(f"📄 Metadata saved to: {os.path.abspath(metadata_file)}")
    
    total_time = time.time() - start_time
    print(f"\n🎉 Process completed successfully in {total_time:.2f}s")
    print(f"📊 Processed {len(docs)} documents → {len(chunks)} chunks → Vector database ready!")

if __name__ == "__main__":
    main()
