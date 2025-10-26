# Best Practices for Embedding Medical Documents

## Overview

This guide provides recommendations for optimally embedding medical knowledge base documents for retrieval.

## 1. Chunking Strategy

### Current Implementation (Good!)

- **Chunk Size**: 1000 characters
- **Overlap**: 200 characters
- **Boundary Detection**: Sentence-aware splitting

### Recommended for Medical Content

#### Option A: Keep Current Settings (Recommended)

```python
chunk_size = 1000  # Good for most medical content
overlap = 200      # Maintains context across chunks
```

**Pros:**

- Captures complete medical concepts (e.g., condition + symptoms + treatment)
- Overlap ensures no information loss at boundaries
- Works well with current embedding model

#### Option B: Semantic Chunking (Advanced)

For better results with complex medical documents:

```python
def semantic_chunk_medical_text(text, target_size=1000, max_size=1500):
    """
    Chunk medical text based on semantic boundaries:
    - Section headers (##, ###)
    - Medical list items (symptoms, treatments)
    - Paragraph breaks with medical topics
    """
    # Split on major section headers
    sections = re.split(r'\n(?=#{1,3}\s+\w+)', text)

    chunks = []
    for section in sections:
        # If section is small enough, keep it
        if len(section) <= max_size:
            chunks.append(section.strip())
        else:
            # Split large sections by subsections or paragraphs
            subsections = re.split(r'\n(?=\*\s+|\d+\.\s+|-\s+)', section)
            current_chunk = ""

            for subsection in subsections:
                if len(current_chunk) + len(subsection) <= max_size:
                    current_chunk += "\n" + subsection
                else:
                    if current_chunk:
                        chunks.append(current_chunk.strip())
                    current_chunk = subsection

            if current_chunk:
                chunks.append(current_chunk.strip())

    return chunks
```

## 2. Embedding Model Selection

### Current: `text-embedding-3-small` ✅

**Specifications:**

- Dimension: 1536
- Cost: $0.02 / 1M tokens
- Performance: Good for most use cases

### Alternative Options:

| Model                  | Dimensions | Cost/1M tokens | Best For                 |
| ---------------------- | ---------- | -------------- | ------------------------ |
| text-embedding-3-small | 1536       | $0.02          | General use (current) ✅ |
| text-embedding-3-large | 3072       | $0.13          | Higher accuracy needed   |
| text-embedding-ada-002 | 1536       | $0.10          | Legacy support           |

**Recommendation**: **Keep text-embedding-3-small** unless you need the highest possible accuracy.

## 3. Metadata Enhancement

### Current Metadata:

```json
{
  "id": "file_chunk_0",
  "source": "sample_medical.txt",
  "chunk_index": 0,
  "text_length": 1000
}
```

### Recommended Enhanced Metadata:

```python
metadata = {
    'id': f"{doc['file']}_{chunk_index}",
    'source': doc['file'],
    'chunk_index': chunk_index,
    'text_length': len(chunk_text),
    'timestamp': time.time(),

    # Medical-specific enhancements:
    'category': detect_medical_category(chunk_text),  # e.g., "Cardiology", "Treatment"
    'entities': extract_medical_entities(chunk_text),  # e.g., ["Hypertension", "ACE inhibitors"]
    'section_header': extract_section_header(chunk_text),  # e.g., "Cardiovascular Conditions"
    'chunk_type': classify_chunk_type(chunk_text)  # e.g., "symptoms", "treatment", "diagnosis"
}
```

## 4. Pre-processing Steps

### Recommended Pre-processing Pipeline:

```python
def preprocess_medical_text(text):
    """Clean and normalize medical text before chunking"""

    # 1. Normalize whitespace (already done ✅)
    text = " ".join(text.split())

    # 2. Preserve medical abbreviations
    # Don't split "e.g.", "i.e.", "Dr.", etc.
    text = text.replace("e.g.", "eg")
    text = text.replace("i.e.", "ie")

    # 3. Normalize medical terms
    # Optional: standardize common variations
    # text = text.replace("heart attack", "myocardial infarction")

    # 4. Remove excessive special characters
    # But keep medical notation (%, °, +/-)

    # 5. Preserve structure
    # Keep bullet points, numbering for lists

    return text
```

## 5. Optimal Workflow for Your Medical Document

### Step-by-Step Process:

```bash
# 1. Ensure your document is in data/ folder
ls data/sample_medical.txt

# 2. Run the loader with default settings
python src/main.py

# This will:
# ✓ Load sample_medical.txt
# ✓ Chunk into ~1000 char pieces with 200 char overlap
# ✓ Generate embeddings using text-embedding-3-small
# ✓ Save to FAISS index (vector_db_index.index)
# ✓ Save metadata (metadata.json)
```

### Expected Results:

- **Document Size**: ~40-50KB (your expanded medical text)
- **Number of Chunks**: ~40-60 chunks
- **Embedding Time**: ~5-10 seconds (batch processing)
- **Total Vectors**: ~40-60 vectors in FAISS index

## 6. Performance Optimization

### Batch Size Tuning:

```python
# Current: batch_size=100 (good!)
embed_documents(chunks, batch_size=100)

# For very large documents (>10,000 chunks):
embed_documents(chunks, batch_size=50)  # Reduce to avoid rate limits

# For small documents (<100 chunks):
embed_documents(chunks, batch_size=20)  # Smaller batches, less memory
```

### Rate Limiting:

```python
# Current implementation has smart retry logic ✅
- Initial batch processing
- Fallback to individual calls on error
- Rate limit delays (0.1s between batches)
```

## 7. Quality Validation

### After Embedding, Validate:

```bash
# 1. Run test retrieval
python test_retrieval.py

# 2. Try various queries:
# - "What are symptoms of hypertension?"
# - "Treatment for diabetes"
# - "Cardiac arrest protocols"
# - "Preventive screening guidelines"
```

### Expected Retrieval Quality:

- **Top-1 Accuracy**: Should return the most relevant chunk
- **Similarity Score**: >0.7 for good matches
- **Response Time**: <500ms for query embedding + search

## 8. Advanced: Hybrid Search (Future Enhancement)

For even better retrieval, consider:

```python
def hybrid_search(query, top_k=5):
    """Combine vector similarity with keyword matching"""

    # 1. Vector search (current)
    vector_results = retriever.search(query, top_k=10)

    # 2. BM25 keyword search
    keyword_results = bm25_search(query, top_k=10)

    # 3. Combine with weighted scores
    final_results = merge_and_rerank(
        vector_results,
        keyword_results,
        vector_weight=0.7,
        keyword_weight=0.3
    )

    return final_results[:top_k]
```

## 9. Monitoring and Maintenance

### Track These Metrics:

```python
{
    "total_chunks": 50,
    "avg_chunk_size": 950,
    "embedding_time": 8.5,
    "index_size_mb": 0.3,
    "queries_tested": 20,
    "avg_similarity_score": 0.78,
    "avg_retrieval_time_ms": 120
}
```

## 10. Quick Reference - Commands

```bash
# Fresh start - rebuild everything
python src/main.py

# Quick test with limited chunks
python src/main.py --test

# Run retrieval demo
python demo_retrieval.py

# Test specific queries
python test_retrieval.py
```

## Summary - What You Should Do

### ✅ Your Current Setup is Good!

Your implementation already follows best practices:

- Appropriate chunk size (1000 chars)
- Good overlap (200 chars)
- Efficient batch processing
- Sentence-aware splitting
- Cost-effective embedding model

### 🚀 Recommended Next Steps:

1. **Run embedding with current settings** (already optimal):

   ```bash
   python src/main.py
   ```

2. **Validate retrieval quality**:

   ```bash
   python demo_retrieval.py
   # Test with medical queries
   ```

3. **Optional enhancements** (if needed):
   - Add medical category detection to metadata
   - Implement hybrid search for better accuracy
   - Add query expansion for synonyms (e.g., "heart attack" → "myocardial infarction")

### 📊 Expected Performance:

- **Embedding Time**: 5-15 seconds for your medical document
- **Storage**: <1 MB for vectors + metadata
- **Query Speed**: <500ms per search
- **Accuracy**: 75-85% top-1 relevance for medical queries

---

**Last Updated**: October 25, 2025
**For**: AI Knowledge Base Loader - Medical Document Embedding
