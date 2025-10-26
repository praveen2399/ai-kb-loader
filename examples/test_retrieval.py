#!/usr/bin/env python3
"""
Test script for the vector retrieval system.
"""

import os
import sys
import tempfile
import json
import numpy as np
from unittest.mock import patch

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from retriever.vector_retriever import VectorRetriever, quick_search
from retriever.utils import VectorDBValidator, safe_load_database
from vectorstore.faiss_indexer import save_to_faiss, load_from_faiss


def test_retriever_basic_functionality():
    """Test basic retriever functionality."""
    print("🧪 Testing Vector Retriever Basic Functionality...")
    
    # Check if test database exists
    if not os.path.exists("vector_db_index.index") or not os.path.exists("metadata.json"):
        print("❌ Test database not found. Run main.py first to create test data.")
        return False
    
    try:
        # Test initialization
        retriever = VectorRetriever()
        
        # Test loading
        if not retriever.load():
            print("❌ Failed to load vector database")
            return False
        
        print("✅ Vector database loaded successfully")
        
        # Test stats
        stats = retriever.get_stats()
        print(f"📊 Stats: {stats['total_vectors']} vectors, {stats['total_chunks']} chunks")
        
        # Test search with a simple query
        test_queries = ["medical", "diagnosis", "treatment"]
        
        for query in test_queries:
            try:
                results = retriever.search(query, top_k=2)
                print(f"🔍 Query '{query}': {len(results)} results")
                
                if results:
                    top_result = results[0]
                    print(f"   Best match: {top_result['metadata'].get('source', 'Unknown')} "
                          f"(similarity: {top_result['similarity_score']:.3f})")
                
            except Exception as e:
                print(f"❌ Search failed for '{query}': {e}")
                return False
        
        print("✅ Basic functionality test passed")
        return True
        
    except Exception as e:
        print(f"❌ Basic functionality test failed: {e}")
        return False


def test_error_handling():
    """Test error handling with invalid inputs."""
    print("\n🧪 Testing Error Handling...")
    
    try:
        # Test with non-existent files
        retriever = VectorRetriever("nonexistent.index", "nonexistent.json")
        if retriever.load():
            print("❌ Should have failed with non-existent files")
            return False
        else:
            print("✅ Correctly handled non-existent files")
        
        # Test validator
        validation = VectorDBValidator.validate_files("nonexistent.index", "nonexistent.json")
        if validation['valid']:
            print("❌ Validator should have detected missing files")
            return False
        else:
            print("✅ Validator correctly detected missing files")
        
        # Test query validation
        from retriever.utils import validate_search_params
        
        # Test empty query
        try:
            validate_search_params("", 5)
            print("❌ Should have failed with empty query")
            return False
        except ValueError:
            print("✅ Correctly rejected empty query")
        
        # Test invalid top_k
        try:
            validate_search_params("test", 0)
            print("❌ Should have failed with top_k=0")
            return False
        except ValueError:
            print("✅ Correctly rejected top_k=0")
        
        print("✅ Error handling test passed")
        return True
        
    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
        return False


def test_quick_search():
    """Test the quick search convenience function."""
    print("\n🧪 Testing Quick Search Function...")
    
    if not os.path.exists("vector_db_index.index") or not os.path.exists("metadata.json"):
        print("⏭️  Skipping quick search test - no test database")
        return True
    
    try:
        results = quick_search("medical diagnosis", top_k=2)
        
        if results:
            print(f"✅ Quick search returned {len(results)} results")
            return True
        else:
            print("⚠️  Quick search returned no results (may be normal)")
            return True
            
    except Exception as e:
        print(f"❌ Quick search test failed: {e}")
        return False


def run_all_tests():
    """Run all tests."""
    print("=== Vector Retrieval System Tests ===\n")
    
    tests = [
        test_retriever_basic_functionality,
        test_error_handling,
        test_quick_search
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed!")
        return True
    else:
        print("❌ Some tests failed")
        return False


if __name__ == "__main__":
    # Set up test environment
    os.environ.setdefault("OPENAI_API_KEY", "test-key")  # Fallback for tests
    
    success = run_all_tests()
    sys.exit(0 if success else 1)