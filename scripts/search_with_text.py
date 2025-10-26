"""
Example: How to access chunk text from retrieval results.
This demonstrates reading chunk text when performing searches.
"""

import os
import sys
from dotenv import load_dotenv

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from retriever.vector_retriever import VectorRetriever
from loader.document_loader import load_documents

# Load environment variables
load_dotenv()


def get_chunk_text_map():
    """
    Create a mapping of chunk IDs to their text content.
    This is useful for retrieving the actual text of search results.
    """
    print("Loading source documents to create chunk text map...")
    docs = load_documents("../data/", max_file_size_mb=50, max_pages=1000)
    
    chunk_text_map = {}
    for doc in docs:
        for i, chunk_text in enumerate(doc['chunks']):
            chunk_id = f"{doc['file']}_{i}"
            chunk_text_map[chunk_id] = chunk_text
    
    print(f"✓ Created text map for {len(chunk_text_map)} chunks\n")
    return chunk_text_map


def search_and_display_with_text(query, top_k=3):
    """
    Perform a search and display results with full text content.
    """
    # Initialize retriever
    retriever = VectorRetriever()
    if not retriever.load():
        print("❌ Failed to load vector database")
        return
    
    # Get chunk text map
    chunk_text_map = get_chunk_text_map()
    
    # Perform search
    print(f"🔎 Searching for: '{query}'...\n")
    results = retriever.search(query, top_k=top_k)
    
    if not results:
        print("😔 No results found")
        return
    
    print(f"🎯 Found {len(results)} results:\n")
    print("="*80)
    
    for i, result in enumerate(results, 1):
        meta = result['metadata']
        chunk_id = meta.get('id', 'Unknown')
        
        print(f"\n📊 RESULT {i}")
        print(f"   Similarity Score: {result['similarity_score']:.3f}")
        print(f"   Distance: {result['distance']:.4f}")
        print(f"   Source: {meta.get('source', 'Unknown')}")
        print(f"   Chunk Index: {meta.get('chunk_index', 'N/A')}")
        print(f"   Chunk ID: {chunk_id}")
        print()
        
        # Get the actual text from our mapping
        if chunk_id in chunk_text_map:
            chunk_text = chunk_text_map[chunk_id]
            print(f"📝 CHUNK TEXT ({len(chunk_text)} characters):")
            print("-" * 80)
            print(chunk_text)
            print("-" * 80)
        else:
            print("⚠️  Chunk text not found in mapping")
        
        print("="*80)


def main():
    print("=== Search with Full Chunk Text Display ===\n")
    
    # Check if vector database exists
    if not os.path.exists("../output/vector_db_index.index") or not os.path.exists("../output/metadata.json"):
        print("❌ Vector database not found!")
        print("📋 Please run 'python src/main.py' first.")
        return
    
    # Example searches
    example_queries = [
        "What are the symptoms of diabetes?",
        "Find a cardiologist",
        "Price of insulin",
        "Emergency phone number"
    ]
    
    print("Example queries you can try:")
    for i, q in enumerate(example_queries, 1):
        print(f"  {i}. {q}")
    print()
    
    # Interactive search
    while True:
        query = input("🤔 Enter your search query (or 'q' to quit): ").strip()
        
        if query.lower() in ['q', 'quit', 'exit']:
            print("\n👋 Goodbye!")
            break
        
        if not query:
            continue
        
        try:
            # Ask for number of results
            top_k_input = input("How many results? (default: 3): ").strip()
            top_k = int(top_k_input) if top_k_input else 3
            
            print()
            search_and_display_with_text(query, top_k=top_k)
            print()
            
        except Exception as e:
            print(f"❌ Error during search: {e}")
            print("Please try again.\n")


if __name__ == "__main__":
    main()
