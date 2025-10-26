"""
Simple script to quickly view chunk content.
Usage: python view_chunk.py <chunk_number>
"""

import json
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from loader.document_loader import load_documents


def load_all_chunks():
    """Load and return all chunks with their text"""
    docs = load_documents("data/", max_file_size_mb=50, max_pages=1000)
    
    chunks = []
    for doc in docs:
        for i, chunk_text in enumerate(doc['chunks']):
            chunks.append({
                'source': doc['file'],
                'chunk_index': i,
                'text': chunk_text,
                'id': f"{doc['file']}_{i}"
            })
    
    return chunks


def display_chunk_info(chunk):
    """Display chunk information"""
    print("="*80)
    print(f"📄 File: {chunk['source']}")
    print(f"🔢 Chunk Index: {chunk['chunk_index']}")
    print(f"🆔 ID: {chunk['id']}")
    print(f"📏 Length: {len(chunk['text'])} characters")
    print("="*80)
    print("\n📝 CHUNK TEXT:\n")
    print(chunk['text'])
    print("\n" + "="*80)


def main():
    if len(sys.argv) > 1:
        # Command line mode - view specific chunk
        try:
            chunk_number = int(sys.argv[1])
            chunks = load_all_chunks()
            
            if 0 <= chunk_number < len(chunks):
                display_chunk_info(chunks[chunk_number])
            else:
                print(f"❌ Chunk number must be between 0 and {len(chunks)-1}")
                print(f"Total chunks available: {len(chunks)}")
        except ValueError:
            print("❌ Please provide a valid chunk number")
            print("Usage: python view_chunk.py <chunk_number>")
    else:
        # Interactive mode
        print("=== Quick Chunk Viewer ===\n")
        print("Loading chunks...")
        chunks = load_all_chunks()
        print(f"✓ Loaded {len(chunks)} chunks\n")
        
        # Show summary
        print("📊 Available chunks:")
        sources = {}
        for chunk in chunks:
            source = chunk['source']
            if source not in sources:
                sources[source] = []
            sources[source].append(chunk['chunk_index'])
        
        for source, indices in sources.items():
            print(f"   • {source}: chunks 0-{len(indices)-1} ({len(indices)} total)")
        
        print(f"\n💡 Total: {len(chunks)} chunks")
        print("\n" + "-"*80)
        
        while True:
            user_input = input("\nEnter chunk number to view (or 'q' to quit): ").strip()
            
            if user_input.lower() in ['q', 'quit', 'exit']:
                print("👋 Goodbye!")
                break
            
            try:
                chunk_num = int(user_input)
                if 0 <= chunk_num < len(chunks):
                    print()
                    display_chunk_info(chunks[chunk_num])
                else:
                    print(f"❌ Please enter a number between 0 and {len(chunks)-1}")
            except ValueError:
                print("❌ Please enter a valid number or 'q' to quit")


if __name__ == "__main__":
    main()
