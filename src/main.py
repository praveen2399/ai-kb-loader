from loader.document_loader import load_documents
from embeddings.embedder import embed_documents
from vectorstore.faiss_indexer import save_to_faiss

def main():
    docs = load_documents("data/")
    print(f"Loaded {len(docs)} documents")

    chunks = [chunk for d in docs for chunk in d['chunks']]
    print(f"Total {len(chunks)} chunks created")

    vectors, ids = embed_documents(chunks)
    print("Embedding complete")

    save_to_faiss(vectors, ids)
    print("FAISS index saved successfully")

if __name__ == "__main__":
    main()
