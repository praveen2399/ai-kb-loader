"""
Simple example: How to programmatically read chunk text
"""

import sys
import os

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from loader.document_loader import load_documents


def example_1_load_all_chunks():
    """Example 1: Load and print all chunks"""
    print("="*80)
    print("EXAMPLE 1: Load All Chunks")
    print("="*80)
    
    # Load documents from data directory
    docs = load_documents("data/")
    
    # Iterate through all documents and chunks
    total_chunks = 0
    for doc in docs:
        print(f"\n📄 File: {doc['file']}")
        print(f"   Chunks: {len(doc['chunks'])}")
        
        for i, chunk_text in enumerate(doc['chunks'][:2]):  # Show first 2 chunks
            print(f"\n   Chunk {i}:")
            print(f"   Length: {len(chunk_text)} chars")
            print(f"   Preview: {chunk_text[:150]}...")
        
        total_chunks += len(doc['chunks'])
    
    print(f"\n✓ Total chunks loaded: {total_chunks}")


def example_2_find_specific_chunk():
    """Example 2: Find and read a specific chunk"""
    print("\n" + "="*80)
    print("EXAMPLE 2: Read Specific Chunk")
    print("="*80)
    
    # Load documents
    docs = load_documents("data/")
    
    # Find chunk from specific file
    target_file = "sample_medical.txt"
    target_index = 5
    
    for doc in docs:
        if doc['file'] == target_file:
            if target_index < len(doc['chunks']):
                chunk_text = doc['chunks'][target_index]
                print(f"\n✓ Found chunk {target_index} from {target_file}")
                print(f"Length: {len(chunk_text)} characters\n")
                print("Text:")
                print("-"*80)
                print(chunk_text)
                print("-"*80)
            else:
                print(f"❌ Chunk index {target_index} not found")
            break


def example_3_create_chunk_dictionary():
    """Example 3: Create a dictionary for easy access"""
    print("\n" + "="*80)
    print("EXAMPLE 3: Create Chunk Dictionary")
    print("="*80)
    
    # Load documents
    docs = load_documents("data/")
    
    # Create dictionary mapping chunk ID to text
    chunk_dict = {}
    
    for doc in docs:
        for i, chunk_text in enumerate(doc['chunks']):
            chunk_id = f"{doc['file']}_{i}"
            chunk_dict[chunk_id] = {
                'text': chunk_text,
                'source': doc['file'],
                'index': i,
                'length': len(chunk_text)
            }
    
    print(f"\n✓ Created dictionary with {len(chunk_dict)} chunks")
    print("\nExample: Access chunk by ID:")
    
    # Example access
    example_id = "sample_medical.txt_0"
    if example_id in chunk_dict:
        chunk = chunk_dict[example_id]
        print(f"\nID: {example_id}")
        print(f"Source: {chunk['source']}")
        print(f"Index: {chunk['index']}")
        print(f"Length: {chunk['length']}")
        print(f"Text preview: {chunk['text'][:150]}...")


def example_4_search_for_keyword():
    """Example 4: Search chunks for a keyword"""
    print("\n" + "="*80)
    print("EXAMPLE 4: Search for Keyword")
    print("="*80)
    
    keyword = "diabetes"
    
    # Load documents
    docs = load_documents("data/")
    
    # Search for keyword
    matches = []
    for doc in docs:
        for i, chunk_text in enumerate(doc['chunks']):
            if keyword.lower() in chunk_text.lower():
                matches.append({
                    'file': doc['file'],
                    'index': i,
                    'text': chunk_text
                })
    
    print(f"\n✓ Found {len(matches)} chunks containing '{keyword}'")
    
    # Show first 3 matches
    for i, match in enumerate(matches[:3], 1):
        print(f"\n--- Match {i} ---")
        print(f"File: {match['file']}")
        print(f"Chunk: {match['index']}")
        print(f"Preview: {match['text'][:200]}...")


def example_5_get_text_for_retrieval():
    """Example 5: Get text for retrieval results"""
    print("\n" + "="*80)
    print("EXAMPLE 5: Map Chunk IDs to Text (for retrieval)")
    print("="*80)
    
    # Load documents
    docs = load_documents("data/")
    
    # Create mapping
    chunk_id_to_text = {}
    for doc in docs:
        for i, chunk_text in enumerate(doc['chunks']):
            chunk_id = f"{doc['file']}_{i}"
            chunk_id_to_text[chunk_id] = chunk_text
    
    print(f"\n✓ Created mapping for {len(chunk_id_to_text)} chunks")
    
    # Simulate retrieval result
    simulated_result_ids = [
        "sample_medical.txt_2",
        "pharmacy_details.txt_5",
        "healthcare_directory.txt_0"
    ]
    
    print("\nSimulated retrieval results:")
    for chunk_id in simulated_result_ids:
        if chunk_id in chunk_id_to_text:
            text = chunk_id_to_text[chunk_id]
            print(f"\n📄 {chunk_id}")
            print(f"   Text: {text[:100]}...")


if __name__ == "__main__":
    print("\n" + "🔍 CHUNK TEXT READING EXAMPLES" + "\n")
    
    # Run all examples
    example_1_load_all_chunks()
    example_2_find_specific_chunk()
    example_3_create_chunk_dictionary()
    example_4_search_for_keyword()
    example_5_get_text_for_retrieval()
    
    print("\n" + "="*80)
    print("✅ All examples completed!")
    print("="*80)
    print("\nKey Takeaway:")
    print("  Use load_documents('data/') to get all chunk text")
    print("  Chunks are in: docs[file_index]['chunks'][chunk_index]")
    print("  Create mappings for easy access by chunk ID")
    print("\nFor more tools, see:")
    print("  - view_chunk.py (interactive viewer)")
    print("  - read_chunks.py (advanced features)")
    print("  - search_with_text.py (search + text display)")
    print("="*80 + "\n")
