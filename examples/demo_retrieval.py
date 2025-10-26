#!/usr/bin/env python3
"""
Demo script to showcase vector retrieval capabilities.
Run this after creating a vector database with main.py
"""

import os
import sys
from dotenv import load_dotenv

# Add src to path so we can import our modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from retriever.vector_retriever import VectorRetriever, quick_search

# Load environment variables
load_dotenv()

def main():
    print("=== AI Knowledge Base Retriever Demo ===\n")
    
    # Check if vector database exists
    if not os.path.exists("output/vector_db_index.index") or not os.path.exists("output/metadata.json"):
        print("❌ Vector database not found!")
        print("📋 Please run 'python src/main.py' first to create the vector database.")
        print("🗂️  Make sure you have documents in the data/ folder.")
        print("🔍 Expected files: output/vector_db_index.index and output/metadata.json")
        return
    
    # Initialize retriever
    print("🔄 Loading vector database...")
    retriever = VectorRetriever()
    
    if not retriever.load():
        print("❌ Failed to load vector database")
        return
    
    # Show database stats
    stats = retriever.get_stats()
    print("✅ Vector database loaded successfully!")
    print(f"📊 Database Stats:")
    print(f"   • Total vectors: {stats['total_vectors']}")
    print(f"   • Vector dimension: {stats['vector_dimension']}")
    print(f"   • Total chunks: {stats['total_chunks']}")
    print(f"   • Sources: {len(stats['sources'])}")
    for source, count in stats['sources'].items():
        print(f"     - {source}: {count} chunks")
    print()
    
    # Interactive search loop
    print("🔍 Enter your search queries (type 'quit' to exit):")
    print("💡 Try asking questions about your documents!\n")
    
    while True:
        try:
            # Get user input
            query = input("🤔 Your question: ").strip()
            
            if query.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            
            if not query:
                continue
            
            print(f"\n🔎 Searching for: '{query}'...")
            
            # Perform search
            results = retriever.search(query, top_k=3)
            
            if not results:
                print("😔 No results found. Try a different query.")
            else:
                print(f"\n🎯 Found {len(results)} relevant results:\n")
                
                for i, result in enumerate(results, 1):
                    meta = result['metadata']
                    print(f"📄 Result {i} (Similarity: {result['similarity_score']:.3f})")
                    print(f"   📁 Source: {meta.get('source', 'Unknown')}")
                    print(f"   🔢 Chunk: {meta.get('chunk_index', 'N/A')}")
                    print(f"   📏 Length: {meta.get('text_length', 'N/A')} characters")
                    print(f"   📊 Distance: {result['distance']:.4f}")
                    print()
            
            print("-" * 50)
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error during search: {e}")
            print("Please try again with a different query.")


def demo_predefined_queries():
    """Run demo with predefined queries for testing"""
    print("=== Running Predefined Query Demo ===\n")
    
    retriever = VectorRetriever()
    if not retriever.load():
        print("❌ Failed to load vector database")
        return
    
    # Sample queries - adjust these based on your document content
    sample_queries = [
        "medical diagnosis",
        "treatment options", 
        "symptoms",
        "patient care",
        "clinical guidelines"
    ]
    
    for query in sample_queries:
        print(f"🔍 Query: '{query}'")
        results = retriever.search(query, top_k=2)
        
        if results:
            for result in results[:1]:  # Show only top result for brevity
                meta = result['metadata']
                print(f"   ✓ Best match: {meta.get('source', 'Unknown')} (similarity: {result['similarity_score']:.3f})")
        else:
            print("   ✗ No results found")
        print()


if __name__ == "__main__":
    # Check for demo mode
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        demo_predefined_queries()
    else:
        main()