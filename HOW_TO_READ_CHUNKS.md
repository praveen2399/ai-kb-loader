# How to Read Text from Chunks

## Overview

The chunk text is stored in the original source files, not in the metadata.json. Here are multiple methods to access chunk text.

---

## Method 1: View Specific Chunks (Simplest)

### Quick View - Interactive

```bash
python view_chunk.py
```

This will:

- Load all chunks from source files
- Show you how many chunks exist
- Let you enter a chunk number to view its full text

### Quick View - Command Line

```bash
# View chunk number 5
python view_chunk.py 5

# View chunk number 0
python view_chunk.py 0
```

**Example Output:**

```
================================================================================
📄 File: sample_medical.txt
🔢 Chunk Index: 5
🆔 ID: sample_medical.txt_5
📏 Length: 1000 characters
================================================================================

📝 CHUNK TEXT:

[Full text of chunk 5 appears here...]

================================================================================
```

---

## Method 2: Advanced Chunk Reader

### Interactive Tool

```bash
python read_chunks.py
```

**Features:**

1. **View specific chunk by index** - Choose file and chunk number
2. **Search by keyword** - Find all chunks containing a word/phrase
3. **List all chunks from a file** - See all chunks from one document
4. **Show first N chunks** - Preview multiple chunks
5. **Export to JSON** - Save all chunks with text to a JSON file

**Example: Search for "diabetes"**

```
Options:
  1. View specific chunk by index
  2. Search chunks by keyword
  ...

Enter your choice: 2
Enter keyword to search: diabetes

✓ Found 12 chunks containing 'diabetes':

--- Match 1 ---
📄 Source: sample_medical.txt
📍 Chunk Index: 3
📏 Length: 998 characters
📝 Text Preview:
--------------------------------------------------------------------------------
Type 2 Diabetes - Definition: Chronic condition affecting blood sugar...
```

---

## Method 3: Search with Full Text Display

### Enhanced Search with Chunk Text

```bash
python search_with_text.py
```

This combines vector search with text display:

- Performs semantic search
- Shows similarity scores
- **Displays the full text of matching chunks**

**Example:**

```bash
python search_with_text.py
```

```
🤔 Enter your search query: symptoms of diabetes
How many results? (default: 3): 3

🔎 Searching for: 'symptoms of diabetes'...

🎯 Found 3 results:

================================================================================

📊 RESULT 1
   Similarity Score: 0.872
   Distance: 0.1280
   Source: sample_medical.txt
   Chunk Index: 2
   Chunk ID: sample_medical.txt_2

📝 CHUNK TEXT (998 characters):
--------------------------------------------------------------------------------
Type 2 Diabetes
- Definition: Chronic condition affecting blood sugar regulation
- Symptoms: Increased thirst, frequent urination, fatigue, blurred vision
- Treatment: Diet modification, exercise, metformin, insulin therapy
- Complications: Cardiovascular disease, kidney damage, nerve damage
--------------------------------------------------------------------------------
```

---

## Method 4: Programmatic Access in Python

### In Your Own Scripts

```python
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from loader.document_loader import load_documents

# Load all documents and chunks
docs = load_documents("data/", max_file_size_mb=50, max_pages=1000)

# Access chunks
for doc in docs:
    print(f"File: {doc['file']}")
    print(f"Number of chunks: {len(doc['chunks'])}")

    for i, chunk_text in enumerate(doc['chunks']):
        print(f"\nChunk {i}:")
        print(f"Length: {len(chunk_text)} characters")
        print(f"Text: {chunk_text[:200]}...")  # First 200 chars
```

### Create a Chunk Text Map

```python
from loader.document_loader import load_documents

def create_chunk_map():
    """Create a dictionary mapping chunk IDs to text"""
    docs = load_documents("data/")

    chunk_map = {}
    for doc in docs:
        for i, text in enumerate(doc['chunks']):
            chunk_id = f"{doc['file']}_{i}"
            chunk_map[chunk_id] = text

    return chunk_map

# Usage
chunk_map = create_chunk_map()

# Get text for a specific chunk
chunk_id = "sample_medical.txt_5"
if chunk_id in chunk_map:
    print(chunk_map[chunk_id])
```

### Access from Retrieval Results

```python
from retriever.vector_retriever import VectorRetriever
from loader.document_loader import load_documents

# Initialize retriever
retriever = VectorRetriever()
retriever.load()

# Create chunk text map
docs = load_documents("data/")
chunk_map = {}
for doc in docs:
    for i, text in enumerate(doc['chunks']):
        chunk_id = f"{doc['file']}_{i}"
        chunk_map[chunk_id] = text

# Search and get text
results = retriever.search("diabetes treatment", top_k=3)

for result in results:
    chunk_id = result['metadata']['id']
    chunk_text = chunk_map.get(chunk_id, "Text not found")

    print(f"Score: {result['similarity_score']}")
    print(f"Text: {chunk_text}")
    print("-" * 80)
```

---

## Method 5: Export All Chunks to JSON

### Save chunks with text for later use

```python
import json
from loader.document_loader import load_documents

# Load and export
docs = load_documents("data/")

all_chunks = []
for doc in docs:
    for i, chunk_text in enumerate(doc['chunks']):
        all_chunks.append({
            'id': f"{doc['file']}_{i}",
            'source': doc['file'],
            'chunk_index': i,
            'text': chunk_text,
            'length': len(chunk_text)
        })

# Save to file
with open('all_chunks_with_text.json', 'w', encoding='utf-8') as f:
    json.dump(all_chunks, f, indent=2, ensure_ascii=False)

print(f"Exported {len(all_chunks)} chunks to all_chunks_with_text.json")
```

**Then read it anytime:**

```python
import json

with open('all_chunks_with_text.json', 'r', encoding='utf-8') as f:
    chunks = json.load(f)

# Access any chunk
print(chunks[5]['text'])  # Text from chunk 5
```

---

## Quick Reference Commands

| Task                     | Command                       |
| ------------------------ | ----------------------------- |
| View chunk 10            | `python view_chunk.py 10`     |
| Interactive chunk viewer | `python view_chunk.py`        |
| Advanced chunk tools     | `python read_chunks.py`       |
| Search with text display | `python search_with_text.py`  |
| Export all chunks        | Use read_chunks.py → Option 5 |

---

## Understanding the Data Flow

```
┌─────────────────────┐
│  Source Files       │
│  - sample_medical   │
│  - healthcare_dir   │
│  - pharmacy_details │
└──────────┬──────────┘
           │
           │ load_documents()
           ▼
┌─────────────────────┐
│  Chunks (in memory) │
│  - Text content     │
│  - Metadata         │
└──────────┬──────────┘
           │
           ├─────────────────┐
           │                 │
           ▼                 ▼
┌──────────────────┐  ┌─────────────────┐
│  FAISS Index     │  │  metadata.json  │
│  (Vectors only)  │  │  (NO text)      │
└──────────────────┘  └─────────────────┘
```

**Key Point:** The actual chunk text is NOT saved to disk after embedding. To access it, you must:

1. Re-load from source files using `load_documents()`
2. Match chunk IDs from metadata with re-loaded chunks
3. Or export chunks with text to a separate JSON file

---

## Pro Tip: Save Chunks with Text (Optional Enhancement)

If you want to save chunk text permanently, modify `src/main.py`:

```python
# After creating chunks, save them with text
chunks_with_text = []
for chunk_text, meta in zip(chunks, metadata):
    chunks_with_text.append({
        **meta,
        'text': chunk_text  # Add the actual text
    })

# Save to separate file
with open('chunks_with_text.json', 'w', encoding='utf-8') as f:
    json.dump(chunks_with_text, f, indent=2, ensure_ascii=False)
```

Then you can always access the text without re-loading source files.

---

## Common Use Cases

### 1. Debug Embeddings

```bash
# See what text was actually embedded
python view_chunk.py 0
```

### 2. Find Content

```bash
# Search for specific medical terms
python read_chunks.py
# Then choose option 2 (Search by keyword)
```

### 3. Build a RAG System

```python
# In your RAG pipeline
from retriever.vector_retriever import VectorRetriever
from loader.document_loader import load_documents

# Get similar chunks
retriever = VectorRetriever()
retriever.load()
results = retriever.search(user_query, top_k=3)

# Get their text
docs = load_documents("data/")
chunk_map = {f"{doc['file']}_{i}": text
             for doc in docs
             for i, text in enumerate(doc['chunks'])}

# Use in prompt
context = "\n\n".join([chunk_map[r['metadata']['id']] for r in results])
prompt = f"Context:\n{context}\n\nQuestion: {user_query}\nAnswer:"
```

---

**Created:** October 25, 2025  
**Updated:** For ai-kb-loader project with medical/healthcare data
