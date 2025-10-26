import os
import json
import numpy as np
from typing import List, Dict, Tuple, Optional
from embeddings.embedder import embed_documents
from vectorstore.chroma_indexer import ChromaIndexer, load_from_chroma, search_chroma_collection
from .utils import (
    validate_search_params, format_error_message,
    DatabaseNotFoundError, DatabaseCorruptedError, QueryEmbeddingError
)
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VectorRetriever:
    """
    A class for retrieving similar documents from a ChromaDB vector database.
    """
    
    def __init__(self, persist_directory: str = "output/chroma_db", collection_name: str = "documents"):
        """
        Initialize the vector retriever.
        
        Args:
            persist_directory: Path to the ChromaDB persistence directory
            collection_name: Name of the ChromaDB collection
        """
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        self.indexer = None
        self.metadata = None
        self.loaded = False
    
    def load(self) -> bool:
        """
        Load the ChromaDB collection and metadata with comprehensive error handling.
        
        Returns:
            bool: True if loading was successful, False otherwise
        """
        try:
            # Check if ChromaDB directory exists
            if not os.path.exists(self.persist_directory):
                raise DatabaseNotFoundError(f"ChromaDB directory not found: {self.persist_directory}")
            
            # Load ChromaDB collection
            self.indexer = load_from_chroma(self.persist_directory, self.collection_name)
            
            # Load metadata if available
            metadata_path = os.path.join(self.persist_directory, "metadata.json")
            if os.path.exists(metadata_path):
                with open(metadata_path, 'r') as f:
                    self.metadata = json.load(f)
            else:
                logger.warning(f"Metadata file not found: {metadata_path}")
                self.metadata = {}
            
            # Get collection stats
            stats = self.indexer.get_collection_stats()
            if stats.get("total_documents", 0) == 0:
                raise DatabaseCorruptedError("ChromaDB collection is empty")
            
            self.loaded = True
            logger.info(f"Successfully loaded ChromaDB collection with {stats.get('total_documents', 0)} documents")
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
            
            # Search ChromaDB collection
            distances, documents, metadatas = search_chroma_collection(
                self.indexer, query_vector, k=top_k
            )
            
            # Format results
            results = []
            for i, (distance, document, metadata) in enumerate(zip(distances, documents, metadatas)):
                # ChromaDB returns distance (lower is better), convert to similarity score
                similarity_score = 1 / (1 + distance) if distance > 0 else 1.0
                
                result = {
                    'rank': i + 1,
                    'content': document,
                    'similarity_score': round(similarity_score, 4),
                    'distance': round(distance, 4),
                    'metadata': metadata or {}
                }
                results.append(result)
            
            logger.info(f"Retrieved {len(results)} results for query: '{query[:50]}...'")
            return results
            
        except QueryEmbeddingError:
            raise
        except Exception as e:
            logger.error(f"Error during search: {e}")
            raise RuntimeError(f"Search failed: {e}")
    
    def get_stats(self) -> Dict:
        """
        Get statistics about the loaded vector database.
        
        Returns:
            Dictionary containing database statistics
        """
        if not self.loaded:
            return {"error": "Database not loaded"}
        
        try:
            stats = self.indexer.get_collection_stats()
            
            # Enhance with metadata if available
            result = {
                'total_vectors': stats.get('total_documents', 0),
                'vector_dimension': stats.get('embedding_dimension', 0),
                'collection_name': stats.get('collection_name', self.collection_name),
                'total_chunks': stats.get('total_documents', 0),
                'sources': {}
            }
            
            # Add source information from metadata if available
            if self.metadata and 'metadatas' in self.metadata:
                source_counts = {}
                for meta in self.metadata['metadatas']:
                    source = meta.get('source', 'unknown')
                    source_counts[source] = source_counts.get(source, 0) + 1
                result['sources'] = source_counts
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {"error": str(e)}
    
    def get_chunk_by_index(self, index: int) -> Optional[Dict]:
        """
        Retrieve a specific chunk by its index.
        
        Args:
            index: Index of the chunk to retrieve
            
        Returns:
            Dictionary containing chunk information or None if not found
        """
        if not self.loaded:
            logger.error("Database not loaded")
            return None
        
        try:
            # Get chunk by ID (assuming IDs are chunk_0, chunk_1, etc.)
            chunk_id = f"chunk_{index}"
            
            # ChromaDB doesn't have direct index access, so we'll use get method
            results = self.indexer.collection.get(
                ids=[chunk_id],
                include=["documents", "metadatas"]
            )
            
            if results and len(results.get("documents", [])) > 0:
                return {
                    'id': chunk_id,
                    'content': results["documents"][0],
                    'metadata': results.get("metadatas", [{}])[0] or {}
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving chunk {index}: {e}")
            return None


def quick_search(query: str, top_k: int = 3, persist_directory: str = "output/chroma_db") -> List[Dict]:
    """
    Quick search function for immediate results without creating a retriever instance.
    
    Args:
        query: Search query string
        top_k: Number of results to return
        persist_directory: Path to ChromaDB persistence directory
        
    Returns:
        List of search results
    """
    try:
        retriever = VectorRetriever(persist_directory)
        
        if not retriever.load():
            logger.error("Failed to load vector database for quick search")
            return []
        
        return retriever.search(query, top_k)
        
    except Exception as e:
        logger.error(f"Quick search failed: {e}")
        return []


def batch_search(queries: List[str], top_k: int = 5, persist_directory: str = "output/chroma_db") -> Dict[str, List[Dict]]:
    """
    Perform batch search for multiple queries efficiently.
    
    Args:
        queries: List of query strings
        top_k: Number of results per query
        persist_directory: Path to ChromaDB persistence directory
        
    Returns:
        Dictionary mapping queries to their results
    """
    try:
        retriever = VectorRetriever(persist_directory)
        
        if not retriever.load():
            logger.error("Failed to load vector database for batch search")
            return {}
        
        results = {}
        for query in queries:
            try:
                results[query] = retriever.search(query, top_k)
            except Exception as e:
                logger.error(f"Error searching for query '{query}': {e}")
                results[query] = []
        
        return results
        
    except Exception as e:
        logger.error(f"Batch search failed: {e}")
        return {}