import os
import json
import faiss
import numpy as np
from typing import List, Dict, Tuple, Optional
from embeddings.embedder import embed_documents
from .utils import (
    safe_load_database, validate_search_params, format_error_message,
    DatabaseNotFoundError, DatabaseCorruptedError, QueryEmbeddingError
)
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VectorRetriever:
    """
    A class for retrieving similar documents from a FAISS vector database.
    """
    
    def __init__(self, index_path: str = "output/vector_db_index.index", metadata_path: str = "output/metadata.json"):
        """
        Initialize the vector retriever.
        
        Args:
            index_path: Path to the FAISS index file
            metadata_path: Path to the metadata JSON file
        """
        self.index_path = index_path
        self.metadata_path = metadata_path
        self.index = None
        self.metadata = None
        self.loaded = False
    
    def load(self) -> bool:
        """
        Load the FAISS index and metadata with comprehensive error handling.
        
        Returns:
            bool: True if loading was successful, False otherwise
        """
        try:
            # Use safe loading with validation
            self.index, self.metadata = safe_load_database(self.index_path, self.metadata_path)
            self.loaded = True
            logger.info(f"Successfully loaded index with {self.index.ntotal} vectors and {len(self.metadata)} metadata entries")
            return True
            
        except (DatabaseNotFoundError, DatabaseCorruptedError) as e:
            logger.error(format_error_message(e))
            return False
        except Exception as e:
            logger.error(f"Unexpected error loading vector database: {e}")
            return False
    
    def _embed_query(self, query: str) -> Optional[np.ndarray]:
        """
        Embed a query string using the same embedder as the documents.
        
        Args:
            query: The query string to embed
            
        Returns:
            numpy array of the query embedding, or None if embedding fails
            
        Raises:
            QueryEmbeddingError: If embedding fails
        """
        try:
            # Use the same embedder as used for documents
            vectors, _ = embed_documents([query])
            if len(vectors) == 0:
                raise QueryEmbeddingError("No embedding returned for query")
            return vectors[0]
        except Exception as e:
            logger.error(f"Error embedding query: {e}")
            raise QueryEmbeddingError(f"Failed to embed query: {e}")
    
    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        Search for similar documents based on a query with comprehensive validation.
        
        Args:
            query: The search query string
            top_k: Number of top similar results to return
            
        Returns:
            List of dictionaries containing search results with metadata and scores
            
        Raises:
            ValueError: If parameters are invalid
            QueryEmbeddingError: If query embedding fails
        """
        # Validate inputs
        validate_search_params(query, top_k)
        
        if not self.loaded:
            raise RuntimeError("Vector retriever not loaded. Call load() first.")
        
        try:
            # Embed the query
            query_vector = self._embed_query(query)
            
            # Perform similarity search
            # Reshape query vector for FAISS
            query_vector = query_vector.reshape(1, -1).astype('float32')
            
            # Search for similar vectors
            search_k = min(top_k, self.index.ntotal)
            distances, indices = self.index.search(query_vector, search_k)
            
            # Prepare results
            results = []
            for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
                if idx >= 0 and idx < len(self.metadata):  # Check for valid index
                    result = {
                        'rank': i + 1,
                        'distance': float(distance),
                        'similarity_score': 1 / (1 + distance),  # Convert distance to similarity
                        'metadata': self.metadata[idx].copy(),
                        'chunk_text': self._get_chunk_text(idx) if hasattr(self, '_get_chunk_text') else None
                    }
                    results.append(result)
                else:
                    logger.warning(f"Invalid index {idx} (metadata length: {len(self.metadata)})")
            
            return results
            
        except QueryEmbeddingError:
            raise  # Re-raise query embedding errors
        except Exception as e:
            logger.error(f"Error during search: {e}")
            raise RuntimeError(f"Search failed: {e}")
    
    def search_by_source(self, query: str, source_filter: str, top_k: int = 5) -> List[Dict]:
        """
        Search for similar documents filtered by source file.
        
        Args:
            query: The search query string
            source_filter: Filter results to only include this source file
            top_k: Number of top similar results to return
            
        Returns:
            List of dictionaries containing filtered search results
        """
        # Get all results first
        all_results = self.search(query, top_k * 3)  # Get more results to filter
        
        # Filter by source
        filtered_results = [
            result for result in all_results 
            if result['metadata'].get('source', '').lower().find(source_filter.lower()) != -1
        ]
        
        # Return top_k filtered results
        return filtered_results[:top_k]
    
    def get_stats(self) -> Dict:
        """
        Get statistics about the loaded vector database.
        
        Returns:
            Dictionary containing database statistics
        """
        if not self.loaded:
            return {"error": "Vector retriever not loaded"}
        
        # Count documents by source
        source_counts = {}
        for meta in self.metadata:
            source = meta.get('source', 'unknown')
            source_counts[source] = source_counts.get(source, 0) + 1
        
        return {
            'total_vectors': self.index.ntotal,
            'total_chunks': len(self.metadata),
            'vector_dimension': self.index.d,
            'sources': source_counts,
            'index_path': self.index_path,
            'metadata_path': self.metadata_path
        }
    
    def format_results(self, results: List[Dict], include_text: bool = True) -> str:
        """
        Format search results for display.
        
        Args:
            results: List of search results from search() method
            include_text: Whether to include chunk text in the output
            
        Returns:
            Formatted string representation of the results
        """
        if not results:
            return "No results found."
        
        formatted = f"Found {len(results)} results:\n\n"
        
        for result in results:
            meta = result['metadata']
            formatted += f"📄 Rank {result['rank']} (Similarity: {result['similarity_score']:.3f})\n"
            formatted += f"   📁 Source: {meta.get('source', 'Unknown')}\n"
            formatted += f"   🔢 Chunk: {meta.get('chunk_index', 'N/A')}\n"
            formatted += f"   📏 Length: {meta.get('text_length', 'N/A')} chars\n"
            
            if include_text and 'chunk_text' in result and result['chunk_text']:
                # Truncate long text for display
                text = result['chunk_text']
                if len(text) > 200:
                    text = text[:200] + "..."
                formatted += f"   📝 Text: {text}\n"
            
            formatted += "\n"
        
        return formatted


# Convenience function for quick retrieval
def quick_search(query: str, top_k: int = 5, 
                index_path: str = "vector_db_index.index", 
                metadata_path: str = "metadata.json") -> List[Dict]:
    """
    Perform a quick search without creating a persistent retriever instance.
    
    Args:
        query: The search query string
        top_k: Number of results to return
        index_path: Path to FAISS index
        metadata_path: Path to metadata file
        
    Returns:
        List of search results
    """
    retriever = VectorRetriever(index_path, metadata_path)
    if retriever.load():
        return retriever.search(query, top_k)
    else:
        return []