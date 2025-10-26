# Vector Retriever Usage Examples

## Quick Start

```python
from src.retriever.vector_retriever import VectorRetriever, quick_search

# Method 1: Quick search (one-liner)
results = quick_search("medical diagnosis", top_k=3)
for result in results:
    print(f"Source: {result['metadata']['source']}")
    print(f"Similarity: {result['similarity_score']:.3f}")
    print()

# Method 2: Using retriever class (recommended for multiple searches)
retriever = VectorRetriever()
if retriever.load():
    results = retriever.search("treatment options", top_k=5)
    print(retriever.format_results(results))
```

## Advanced Usage

```python
# Search with source filtering
results = retriever.search_by_source("symptoms", "medical_manual.pdf", top_k=3)

# Get database statistics
stats = retriever.get_stats()
print(f"Total documents: {len(stats['sources'])}")
print(f"Total chunks: {stats['total_chunks']}")

# Error handling
try:
    results = retriever.search("", top_k=5)  # Empty query
except ValueError as e:
    print(f"Invalid query: {e}")
```

## Running the Demo

```bash
# Interactive demo
python demo_retrieval.py

# Automated demo with sample queries
python demo_retrieval.py --demo

# Run tests
python test_retrieval.py
```

## Project Structure

```
src/
├── retriever/
│   ├── __init__.py
│   ├── vector_retriever.py    # Main retriever class
│   └── utils.py              # Validation and error handling
├── embeddings/
│   └── embedder.py           # Enhanced with query embedding
└── vectorstore/
    └── faiss_indexer.py      # Enhanced with loading functions
```

## Error Handling

The vector retriever includes comprehensive error handling:

- **DatabaseNotFoundError**: Vector database files missing
- **DatabaseCorruptedError**: Database files corrupted
- **QueryEmbeddingError**: Failed to embed query
- **ValueError**: Invalid search parameters

## Performance Tips

1. **Reuse retriever instances** for multiple searches
2. **Use appropriate top_k values** (3-10 typically sufficient)
3. **Monitor OpenAI API usage** for query embedding
4. **Check database consistency** if getting unexpected results

## Troubleshooting

- **No results**: Try broader or simpler queries
- **Low similarity scores**: May indicate query-document mismatch
- **API errors**: Check OPENAI_API_KEY environment variable
- **File not found**: Run `python src/main.py` to create database first
