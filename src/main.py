import time
import os
from loader.document_loader import load_documents
from embeddings.embedder import embed_documents
from vectorstore.faiss_indexer import save_to_faiss

def main():
    start_time = time.time()
    
    print("=== AI Knowledge Base Loader ===")
    
    # Check if we have documents to process
    data_dir = "data/"  # Relative to project root
    if not os.path.exists(data_dir):
        os.makedirs(data_dir, exist_ok=True)
    
    print("Step 1/4: Loading documents...")
    step_start = time.time()
    
    docs = load_documents(data_dir)
    
    if not docs:
        print("\n❌ No documents found!")
        print(f"📁 Please add PDF or DOCX files to: {os.path.abspath(data_dir)}")
        print("📋 Supported formats: .pdf, .docx")
        print("💡 Example: Copy your documents to the data/ folder and run again")
        return
    
    print(f"✓ Loaded {len(docs)} documents ({time.time() - step_start:.2f}s)")

    print("\nStep 2/4: Processing chunks...")
    step_start = time.time()
    chunks = [chunk for d in docs for chunk in d['chunks']]
    
    if not chunks:
        print("❌ No text chunks created from documents")
        return
        
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

    print("\nStep 4/4: Saving FAISS index...")
    step_start = time.time()
    save_to_faiss(vectors, ids, "faiss_index.index")
    print(f"✓ FAISS index saved ({time.time() - step_start:.2f}s)")
    
    total_time = time.time() - start_time
    print(f"\n🎉 Process completed successfully in {total_time:.2f}s")
    print(f"📊 Processed {len(docs)} documents → {len(chunks)} chunks → Vector database ready!")

if __name__ == "__main__":
    main()
