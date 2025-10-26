# Quick Start: Reading Chunk Text

## ✅ I've created 3 tools for you to read chunk text!

### 🚀 Quick Commands

#### 1️⃣ View a Specific Chunk (Fastest)

```bash
# View chunk number 0
/Users/praveenprasannakumar/Desktop/Learnings/AIML-Personal_Project/ai-kb-loader/venv/bin/python view_chunk.py 0

# View chunk number 10
/Users/praveenprasannakumar/Desktop/Learnings/AIML-Personal_Project/ai-kb-loader/venv/bin/python view_chunk.py 10

# Interactive mode - browse all chunks
/Users/praveenprasannakumar/Desktop/Learnings/AIML-Personal_Project/ai-kb-loader/venv/bin/python view_chunk.py
```

**Example Output:**

```
================================================================================
📄 File: healthcare_directory.txt
🔢 Chunk Index: 0
🆔 ID: healthcare_directory.txt_0
📏 Length: 1000 characters
================================================================================

📝 CHUNK TEXT:

Healthcare Provider Directory - Medical Facilities and Specialists
...
[Full text displayed here]
...
================================================================================
```

#### 2️⃣ Advanced Chunk Reader (Most Features)

```bash
/Users/praveenprasannakumar/Desktop/Learnings/AIML-Personal_Project/ai-kb-loader/venv/bin/python read_chunks.py
```

**Features:**

- ✅ View specific chunks
- ✅ **Search by keyword** (find all chunks with "diabetes", "pharmacy", etc.)
- ✅ List all chunks from one file
- ✅ Preview first N chunks
- ✅ Export everything to JSON

#### 3️⃣ Search with Full Text (Best for Queries)

```bash
/Users/praveenprasannakumar/Desktop/Learnings/AIML-Personal_Project/ai-kb-loader/venv/bin/python search_with_text.py
```

**What it does:**

- Performs vector similarity search
- Shows relevance scores
- **Displays the complete text** of matching chunks

---

## 📊 Your Current Data

After running `python src/main.py`, you have:

| Source File              | Chunks   | Total Size |
| ------------------------ | -------- | ---------- |
| healthcare_directory.txt | ~30      | 20KB       |
| sample_medical.txt       | ~35      | 29KB       |
| pharmacy_details.txt     | ~40      | 28KB       |
| **TOTAL**                | **~105** | **~75KB**  |

---

## 🎯 Common Tasks

### Task: View chunk #5

```bash
/Users/praveenprasannakumar/Desktop/Learnings/AIML-Personal_Project/ai-kb-loader/venv/bin/python view_chunk.py 5
```

### Task: Find all chunks mentioning "diabetes"

```bash
/Users/praveenprasannakumar/Desktop/Learnings/AIML-Personal_Project/ai-kb-loader/venv/bin/python read_chunks.py
# Then select option 2 (Search by keyword)
# Enter: diabetes
```

### Task: See what text matches a query

```bash
/Users/praveenprasannakumar/Desktop/Learnings/AIML-Personal_Project/ai-kb-loader/venv/bin/python search_with_text.py
# Enter query: "insulin price"
# See the exact text that was retrieved
```

### Task: Export all chunks to JSON

```bash
/Users/praveenprasannakumar/Desktop/Learnings/AIML-Personal_Project/ai-kb-loader/venv/bin/python read_chunks.py
# Select option 5 (Export to JSON)
# All chunks with text saved to chunks_export.json
```

---

## 💡 Pro Tips

### Shortcut Alias (Optional)

Add to your `~/.zshrc`:

```bash
alias view-chunk='/Users/praveenprasannakumar/Desktop/Learnings/AIML-Personal_Project/ai-kb-loader/venv/bin/python /Users/praveenprasannakumar/Desktop/Learnings/AIML-Personal_Project/ai-kb-loader/view_chunk.py'
```

Then just use:

```bash
view-chunk 0
view-chunk 10
```

### Use in Your Code

```python
# Add this to any Python script
import sys
sys.path.append('src')
from loader.document_loader import load_documents

# Load all chunks
docs = load_documents("data/")

# Access any chunk
for doc in docs:
    for i, chunk_text in enumerate(doc['chunks']):
        print(f"Chunk {i}: {chunk_text[:100]}...")
```

---

## 📚 Full Documentation

See `HOW_TO_READ_CHUNKS.md` for complete details including:

- Programmatic access patterns
- Integration with retrieval
- RAG system examples
- All available methods

---

## ❓ FAQ

**Q: Where is the chunk text stored?**  
A: The text is in your original files (`data/*.txt`). The tools re-load and chunk them when you run.

**Q: Why isn't text in metadata.json?**  
A: To save space. The FAISS index stores vectors, metadata stores references. The text can always be re-loaded from source files.

**Q: How do I get text for retrieval results?**  
A: Use `search_with_text.py` - it automatically matches retrieval results with their source text.

**Q: Can I save chunks with text permanently?**  
A: Yes! Use `read_chunks.py` → Option 5 to export to JSON. Then you have a permanent copy.

---

**Created:** October 25, 2025  
**Project:** ai-kb-loader
