#!/usr/bin/env python3
"""
Simple test script to debug document content retrieval
"""

import os
import sys
from dotenv import load_dotenv

# Add src to path so we can import our modules
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from retriever.vector_retriever import VectorRetriever

# Load environment variables
load_dotenv()

def test_content_retrieval():
    print("=== Testing Document Content Retrieval ===\n")
    
    # Initialize retriever
    print("🔄 Loading vector database...")
    retriever = VectorRetriever()
    
    if not retriever.load():
        print("❌ Failed to load vector database")
        return
    
    print("✅ Vector database loaded successfully!")
    
    # Test search with debug output
    query = "hospital"
    print(f"\n🔍 Testing search with query: '{query}'")
    
    try:
        results = retriever.search(query, top_k=2)
        
        print(f"📊 Retrieved {len(results)} results")
        
        for i, result in enumerate(results, 1):
            print(f"\n📄 Result {i}:")
            print(f"   🔑 Keys in result: {list(result.keys())}")
            
            if 'content' in result:
                content = result['content']
                print(f"   📝 Content type: {type(content)}")
                print(f"   📏 Content length: {len(content) if content else 'None'}")
                if content:
                    print(f"   📖 First 200 chars: {content[:200]}...")
                else:
                    print(f"   ❌ Content is empty or None")
            else:
                print(f"   ❌ No 'content' key found in result")
            
            print(f"   📊 Metadata: {result.get('metadata', {})}")
            print(f"   📈 Similarity: {result.get('similarity_score', 'N/A')}")
            
    except Exception as e:
        print(f"❌ Error during search: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_content_retrieval()