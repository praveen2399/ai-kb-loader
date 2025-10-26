"""
Utility script to rea    docs = load_documents("../data/", max_file_size_mb=50, max_pages=200) and display chunk text from the knowledge base.

This script demonstrates different ways to access the actual text content
from your embedded chunks.
"""

import json
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from loader.document_loader import load_documents, chunk_text


def read_chunks_from_source():
    """
    Method 1: Re-load and chunk the original documents
    This is the most reliable way to get the exact text that was embedded.
    """
    print("=== Method 1: Reading chunks from source files ===\n")
    
    # Load documents using the same method as main.py
    docs = load_documents("data/", max_file_size_mb=50, max_pages=1000)
    
    all_chunks = []
    for doc in docs:
        for i, chunk_text in enumerate(doc['chunks']):
            all_chunks.append({
                'source': doc['file'],
                'chunk_index': i,
                'text': chunk_text,
                'length': len(chunk_text)
            })
    
    return all_chunks


def display_chunk(chunk, show_full_text=False):
    """Display a chunk with formatting"""
    print(f"📄 Source: {chunk['source']}")
    print(f"📍 Chunk Index: {chunk['chunk_index']}")
    print(f"📏 Length: {chunk['length']} characters")
    print(f"📝 Text Preview:")
    print("-" * 80)
    
    if show_full_text:
        print(chunk['text'])
    else:
        # Show first 300 characters
        preview = chunk['text'][:300]
        print(preview)
        if len(chunk['text']) > 300:
            print(f"\n... ({len(chunk['text']) - 300} more characters)")
    
    print("-" * 80)
    print()


def search_chunks_by_keyword(chunks, keyword):
    """Search for chunks containing a specific keyword"""
    matching_chunks = []
    
    for chunk in chunks:
        if keyword.lower() in chunk['text'].lower():
            matching_chunks.append(chunk)
    
    return matching_chunks


def get_chunk_by_index(chunks, source_file, chunk_index):
    """Get a specific chunk by source file and index"""
    for chunk in chunks:
        if chunk['source'] == source_file and chunk['chunk_index'] == chunk_index:
            return chunk
    return None


def main():
    print("=== Chunk Text Reader ===\n")
    
    # Load all chunks from source files
    print("Loading chunks from source documents...")
    chunks = read_chunks_from_source()
    print(f"✓ Loaded {len(chunks)} total chunks\n")
    
    # Show statistics
    sources = {}
    for chunk in chunks:
        source = chunk['source']
        sources[source] = sources.get(source, 0) + 1
    
    print("📊 Chunks by source file:")
    for source, count in sources.items():
        print(f"   • {source}: {count} chunks")
    print()
    
    # Interactive mode
    while True:
        print("\n" + "="*80)
        print("Options:")
        print("  1. View specific chunk by index")
        print("  2. Search chunks by keyword")
        print("  3. List all chunks from a file")
        print("  4. Show first N chunks")
        print("  5. Export all chunks to JSON")
        print("  6. Quit")
        print("="*80)
        
        choice = input("\nEnter your choice (1-6): ").strip()
        
        if choice == '1':
            # View specific chunk
            print("\nAvailable files:")
            for i, source in enumerate(sources.keys(), 1):
                print(f"  {i}. {source}")
            
            file_choice = input("\nEnter file number: ").strip()
            try:
                source_file = list(sources.keys())[int(file_choice) - 1]
                chunk_idx = int(input(f"Enter chunk index (0-{sources[source_file]-1}): "))
                
                chunk = get_chunk_by_index(chunks, source_file, chunk_idx)
                if chunk:
                    display_chunk(chunk, show_full_text=True)
                else:
                    print("❌ Chunk not found")
            except (ValueError, IndexError):
                print("❌ Invalid input")
        
        elif choice == '2':
            # Search by keyword
            keyword = input("\nEnter keyword to search: ").strip()
            if keyword:
                matches = search_chunks_by_keyword(chunks, keyword)
                print(f"\n✓ Found {len(matches)} chunks containing '{keyword}':\n")
                
                for i, chunk in enumerate(matches[:5], 1):  # Show first 5
                    print(f"\n--- Match {i} ---")
                    display_chunk(chunk, show_full_text=False)
                
                if len(matches) > 5:
                    print(f"\n... and {len(matches) - 5} more matches")
        
        elif choice == '3':
            # List all chunks from a file
            print("\nAvailable files:")
            for i, source in enumerate(sources.keys(), 1):
                print(f"  {i}. {source}")
            
            file_choice = input("\nEnter file number: ").strip()
            try:
                source_file = list(sources.keys())[int(file_choice) - 1]
                file_chunks = [c for c in chunks if c['source'] == source_file]
                
                print(f"\n✓ {len(file_chunks)} chunks from {source_file}:\n")
                for chunk in file_chunks:
                    display_chunk(chunk, show_full_text=False)
            except (ValueError, IndexError):
                print("❌ Invalid input")
        
        elif choice == '4':
            # Show first N chunks
            n = input("\nHow many chunks to display? ").strip()
            try:
                n = int(n)
                for chunk in chunks[:n]:
                    display_chunk(chunk, show_full_text=False)
            except ValueError:
                print("❌ Invalid number")
        
        elif choice == '5':
            # Export to JSON
            output_file = input("\nEnter output filename (default: chunks_export.json): ").strip()
            if not output_file:
                output_file = "chunks_export.json"
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(chunks, f, indent=2, ensure_ascii=False)
            
            print(f"✓ Exported {len(chunks)} chunks to {output_file}")
        
        elif choice == '6':
            print("\n👋 Goodbye!")
            break
        
        else:
            print("❌ Invalid choice")


if __name__ == "__main__":
    main()
