import faiss
import numpy as np
import os
from typing import Tuple, Optional, List
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def save_to_faiss(vectors, ids, output_path="vector_db_index.index"):
    """
    Save vectors to a FAISS index file.
    
    Args:
        vectors: Array of embedding vectors
        ids: List of vector IDs
        output_path: Path to save the FAISS index
    """
    try:
        dim = len(vectors[0])
        index = faiss.IndexFlatL2(dim)
        index.add(np.array(vectors).astype("float32"))
        faiss.write_index(index, output_path)
        logger.info(f"FAISS index saved at {output_path}")
        logger.info(f"Index contains {index.ntotal} vectors with dimension {dim}")
    except Exception as e:
        logger.error(f"Error saving FAISS index: {e}")
        raise


def load_from_faiss(index_path: str = "vector_db_index.index") -> Optional[faiss.Index]:
    """
    Load a FAISS index from file.
    
    Args:
        index_path: Path to the FAISS index file
        
    Returns:
        Loaded FAISS index or None if loading fails
    """
    try:
        if not os.path.exists(index_path):
            logger.error(f"FAISS index file not found: {index_path}")
            return None
        
        index = faiss.read_index(index_path)
        logger.info(f"Successfully loaded FAISS index from {index_path}")
        logger.info(f"Index contains {index.ntotal} vectors with dimension {index.d}")
        return index
        
    except Exception as e:
        logger.error(f"Error loading FAISS index: {e}")
        return None


def search_faiss_index(index: faiss.Index, query_vector: np.ndarray, k: int = 5) -> Tuple[np.ndarray, np.ndarray]:
    """
    Search for similar vectors in a FAISS index.
    
    Args:
        index: FAISS index to search
        query_vector: Query vector (should be 2D array with shape (1, dimension))
        k: Number of nearest neighbors to return
        
    Returns:
        Tuple of (distances, indices) arrays
    """
    try:
        # Ensure query vector is the right shape and type
        if query_vector.ndim == 1:
            query_vector = query_vector.reshape(1, -1)
        query_vector = query_vector.astype('float32')
        
        # Perform search
        distances, indices = index.search(query_vector, min(k, index.ntotal))
        return distances, indices
        
    except Exception as e:
        logger.error(f"Error searching FAISS index: {e}")
        return np.array([[]]), np.array([[]])


def get_index_stats(index: faiss.Index) -> dict:
    """
    Get statistics about a FAISS index.
    
    Args:
        index: FAISS index
        
    Returns:
        Dictionary containing index statistics
    """
    return {
        'total_vectors': index.ntotal,
        'dimension': index.d,
        'index_type': type(index).__name__,
        'is_trained': index.is_trained if hasattr(index, 'is_trained') else True
    }
