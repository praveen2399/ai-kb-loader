import chromadb
import numpy as np
import os
from typing import List, Dict, Optional, Tuple
import logging
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ChromaIndexer:
    """
    ChromaDB-based vector store implementation to replace FAISS.
    """
    
    def __init__(self, persist_directory: str = "output/chroma_db"):
        """
        Initialize ChromaDB client with persistence.
        
        Args:
            persist_directory: Directory to persist ChromaDB data
        """
        self.persist_directory = persist_directory
        self.client = None
        self.collection = None
        
        # Ensure output directory exists
        os.makedirs(persist_directory, exist_ok=True)
    
    def initialize_client(self):
        """Initialize ChromaDB client with persistence settings."""
        try:
            # Create persistent client
            self.client = chromadb.PersistentClient(path=self.persist_directory)
            logger.info(f"ChromaDB client initialized with persistence at {self.persist_directory}")
        except Exception as e:
            logger.error(f"Error initializing ChromaDB client: {e}")
            raise
    
    def create_collection(self, collection_name: str = "documents", reset: bool = False):
        """
        Create or get a ChromaDB collection.
        
        Args:
            collection_name: Name of the collection
            reset: Whether to reset/recreate the collection if it exists
        """
        try:
            if self.client is None:
                self.initialize_client()
            
            if reset:
                try:
                    self.client.delete_collection(collection_name)
                    logger.info(f"Deleted existing collection: {collection_name}")
                except Exception:
                    pass  # Collection might not exist
            
            # Create or get collection
            self.collection = self.client.get_or_create_collection(
                name=collection_name,
                metadata={"description": "Document embeddings collection"}
            )
            logger.info(f"Collection '{collection_name}' ready with {self.collection.count()} documents")
            
        except Exception as e:
            logger.error(f"Error creating collection: {e}")
            raise
    
    def add_documents(self, embeddings: List[List[float]], documents: List[str], 
                     metadatas: List[Dict], ids: List[str]):
        """
        Add documents to the ChromaDB collection.
        
        Args:
            embeddings: List of embedding vectors
            documents: List of document texts
            metadatas: List of metadata dictionaries
            ids: List of unique document IDs
        """
        try:
            if self.collection is None:
                self.create_collection()
            
            # Add documents to collection
            self.collection.add(
                embeddings=embeddings,
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            
            logger.info(f"Added {len(documents)} documents to ChromaDB collection")
            logger.info(f"Collection now contains {self.collection.count()} total documents")
            
        except Exception as e:
            logger.error(f"Error adding documents to ChromaDB: {e}")
            raise
    
    def search(self, query_embeddings: List[List[float]], n_results: int = 5) -> Dict:
        """
        Search for similar documents in the collection.
        
        Args:
            query_embeddings: Query embedding vectors
            n_results: Number of results to return
            
        Returns:
            Dictionary containing search results
        """
        try:
            if self.collection is None:
                raise ValueError("Collection not initialized. Call create_collection() first.")
            
            results = self.collection.query(
                query_embeddings=query_embeddings,
                n_results=min(n_results, self.collection.count())
            )
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching ChromaDB: {e}")
            raise
    
    def get_collection_stats(self) -> Dict:
        """
        Get statistics about the current collection.
        
        Returns:
            Dictionary containing collection statistics
        """
        if self.collection is None:
            return {"error": "No collection loaded"}
        
        try:
            count = self.collection.count()
            peek = self.collection.peek(limit=1)
            
            stats = {
                "total_documents": count,
                "collection_name": self.collection.name,
                "has_documents": count > 0
            }
            
            if peek and len(peek["embeddings"]) > 0:
                stats["embedding_dimension"] = len(peek["embeddings"][0])
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting collection stats: {e}")
            return {"error": str(e)}


def save_to_chroma(vectors: np.ndarray, chunks: List[str], metadatas: List[Dict], 
                   persist_directory: str = "output/chroma_db", collection_name: str = "documents"):
    """
    Save vectors and documents to ChromaDB.
    
    Args:
        vectors: Array of embedding vectors
        chunks: List of document chunks
        metadatas: List of metadata dictionaries for each chunk
        persist_directory: Directory to persist ChromaDB data
        collection_name: Name of the ChromaDB collection
    """
    try:
        # Initialize indexer
        indexer = ChromaIndexer(persist_directory)
        indexer.create_collection(collection_name, reset=True)
        
        # Convert numpy array to list and generate IDs
        embeddings = vectors.tolist()
        ids = [f"chunk_{i}" for i in range(len(chunks))]
        
        # Add documents to ChromaDB
        indexer.add_documents(
            embeddings=embeddings,
            documents=chunks,
            metadatas=metadatas,
            ids=ids
        )
        
        logger.info(f"Successfully saved {len(chunks)} documents to ChromaDB")
        
        # Save additional metadata for compatibility
        metadata_path = os.path.join(persist_directory, "metadata.json")
        with open(metadata_path, 'w') as f:
            json.dump({
                "total_chunks": len(chunks),
                "embedding_dimension": len(vectors[0]) if len(vectors) > 0 else 0,
                "collection_name": collection_name,
                "metadatas": metadatas
            }, f, indent=2)
        
        return indexer
        
    except Exception as e:
        logger.error(f"Error saving to ChromaDB: {e}")
        raise


def load_from_chroma(persist_directory: str = "output/chroma_db", 
                     collection_name: str = "documents") -> ChromaIndexer:
    """
    Load an existing ChromaDB collection.
    
    Args:
        persist_directory: Directory where ChromaDB data is persisted
        collection_name: Name of the ChromaDB collection to load
        
    Returns:
        ChromaIndexer instance with loaded collection
    """
    try:
        if not os.path.exists(persist_directory):
            raise FileNotFoundError(f"ChromaDB directory not found: {persist_directory}")
        
        indexer = ChromaIndexer(persist_directory)
        indexer.initialize_client()
        
        # Get existing collection
        indexer.collection = indexer.client.get_collection(collection_name)
        
        stats = indexer.get_collection_stats()
        logger.info(f"Loaded ChromaDB collection: {stats}")
        
        return indexer
        
    except Exception as e:
        logger.error(f"Error loading from ChromaDB: {e}")
        raise


def search_chroma_collection(indexer: ChromaIndexer, query_vector: np.ndarray, 
                           k: int = 5) -> Tuple[List[float], List[str], List[Dict]]:
    """
    Search ChromaDB collection for similar vectors.
    
    Args:
        indexer: ChromaIndexer instance
        query_vector: Query embedding vector
        k: Number of results to return
        
    Returns:
        Tuple of (distances, documents, metadatas)
    """
    try:
        # Ensure query vector is the right format
        if query_vector.ndim == 1:
            query_embeddings = [query_vector.tolist()]
        else:
            query_embeddings = query_vector.tolist()
        
        results = indexer.search(query_embeddings, n_results=k)
        
        # Extract results
        distances = results.get("distances", [[]])[0] if results.get("distances") else []
        documents = results.get("documents", [[]])[0] if results.get("documents") else []
        metadatas = results.get("metadatas", [[]])[0] if results.get("metadatas") else []
        
        return distances, documents, metadatas
        
    except Exception as e:
        logger.error(f"Error searching ChromaDB collection: {e}")
        return [], [], []