"""
Utilities for vector retrieval system including validation and error handling.
"""

import os
import json
import faiss
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class VectorDBValidator:
    """Validator for vector database integrity and consistency."""
    
    @staticmethod
    def validate_files(index_path: str, metadata_path: str) -> Dict[str, Any]:
        """
        Validate that required files exist and are accessible.
        
        Args:
            index_path: Path to FAISS index file
            metadata_path: Path to metadata JSON file
            
        Returns:
            Dictionary with validation results
        """
        validation = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'index_exists': False,
            'metadata_exists': False,
            'index_readable': False,
            'metadata_readable': False
        }
        
        # Check if index file exists
        if os.path.exists(index_path):
            validation['index_exists'] = True
            try:
                # Try to read the index
                faiss.read_index(index_path)
                validation['index_readable'] = True
            except Exception as e:
                validation['errors'].append(f"Index file corrupted: {e}")
                validation['valid'] = False
        else:
            validation['errors'].append(f"Index file not found: {index_path}")
            validation['valid'] = False
        
        # Check if metadata file exists
        if os.path.exists(metadata_path):
            validation['metadata_exists'] = True
            try:
                # Try to read the metadata
                with open(metadata_path, 'r', encoding='utf-8') as f:
                    json.load(f)
                validation['metadata_readable'] = True
            except Exception as e:
                validation['errors'].append(f"Metadata file corrupted: {e}")
                validation['valid'] = False
        else:
            validation['errors'].append(f"Metadata file not found: {metadata_path}")
            validation['valid'] = False
        
        return validation
    
    @staticmethod
    def validate_consistency(index_path: str, metadata_path: str) -> Dict[str, Any]:
        """
        Validate consistency between FAISS index and metadata.
        
        Args:
            index_path: Path to FAISS index file
            metadata_path: Path to metadata JSON file
            
        Returns:
            Dictionary with consistency validation results
        """
        validation = {
            'consistent': True,
            'errors': [],
            'warnings': [],
            'index_count': 0,
            'metadata_count': 0
        }
        
        try:
            # Load index and get vector count
            index = faiss.read_index(index_path)
            validation['index_count'] = index.ntotal
            
            # Load metadata and get count
            with open(metadata_path, 'r', encoding='utf-8') as f:
                metadata_content = json.load(f)
                metadata_list = metadata_content.get('metadata', [])
                validation['metadata_count'] = len(metadata_list)
            
            # Check if counts match
            if validation['index_count'] != validation['metadata_count']:
                validation['consistent'] = False
                validation['errors'].append(
                    f"Mismatch: {validation['index_count']} vectors vs {validation['metadata_count']} metadata entries"
                )
            
            # Check vector dimension
            if index.d != 1536:  # text-embedding-3-small dimension
                validation['warnings'].append(
                    f"Unexpected vector dimension: {index.d} (expected 1536)"
                )
                
        except Exception as e:
            validation['consistent'] = False
            validation['errors'].append(f"Error during consistency check: {e}")
        
        return validation
    
    @staticmethod
    def validate_query(query: str) -> Dict[str, Any]:
        """
        Validate search query input.
        
        Args:
            query: Query string to validate
            
        Returns:
            Dictionary with query validation results
        """
        validation = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        if not query or not query.strip():
            validation['valid'] = False
            validation['errors'].append("Query cannot be empty")
            return validation
        
        # Check query length
        if len(query.strip()) < 3:
            validation['warnings'].append("Very short queries may not return relevant results")
        
        if len(query) > 5000:
            validation['warnings'].append("Very long queries may be truncated")
        
        return validation


class RetrieverError(Exception):
    """Custom exception for retrieval system errors."""
    pass


class DatabaseNotFoundError(RetrieverError):
    """Raised when vector database files are not found."""
    pass


class DatabaseCorruptedError(RetrieverError):
    """Raised when vector database files are corrupted."""
    pass


class QueryEmbeddingError(RetrieverError):
    """Raised when query embedding fails.""" 
    pass


def safe_load_database(index_path: str, metadata_path: str) -> tuple:
    """
    Safely load database with comprehensive error handling.
    
    Args:
        index_path: Path to FAISS index
        metadata_path: Path to metadata JSON
        
    Returns:
        Tuple of (index, metadata) or raises appropriate exception
        
    Raises:
        DatabaseNotFoundError: If files don't exist
        DatabaseCorruptedError: If files are corrupted
    """
    # Validate files exist and are readable
    file_validation = VectorDBValidator.validate_files(index_path, metadata_path)
    
    if not file_validation['valid']:
        missing_files = []
        if not file_validation['index_exists']:
            missing_files.append(index_path)
        if not file_validation['metadata_exists']:
            missing_files.append(metadata_path)
        
        if missing_files:
            raise DatabaseNotFoundError(f"Database files not found: {', '.join(missing_files)}")
        else:
            raise DatabaseCorruptedError(f"Database files corrupted: {', '.join(file_validation['errors'])}")
    
    # Check consistency
    consistency_validation = VectorDBValidator.validate_consistency(index_path, metadata_path)
    
    if not consistency_validation['consistent']:
        logger.warning(f"Database consistency issues: {', '.join(consistency_validation['errors'])}")
        # Don't fail on consistency issues, just log warnings
    
    try:
        # Load the files
        index = faiss.read_index(index_path)
        
        with open(metadata_path, 'r', encoding='utf-8') as f:
            metadata_content = json.load(f)
            metadata = metadata_content.get('metadata', [])
        
        return index, metadata
        
    except Exception as e:
        raise DatabaseCorruptedError(f"Failed to load database: {e}")


def validate_search_params(query: str, top_k: int) -> None:
    """
    Validate search parameters.
    
    Args:
        query: Search query
        top_k: Number of results to return
        
    Raises:
        ValueError: If parameters are invalid
    """
    query_validation = VectorDBValidator.validate_query(query)
    
    if not query_validation['valid']:
        raise ValueError(f"Invalid query: {', '.join(query_validation['errors'])}")
    
    if top_k <= 0:
        raise ValueError("top_k must be positive")
    
    if top_k > 1000:
        logger.warning(f"Large top_k value ({top_k}) may impact performance")


def format_error_message(error: Exception) -> str:
    """
    Format error messages for user display.
    
    Args:
        error: Exception to format
        
    Returns:
        User-friendly error message
    """
    if isinstance(error, DatabaseNotFoundError):
        return (
            "❌ Vector database not found.\n"
            "💡 Run 'python src/main.py' first to create the database.\n"
            "📁 Make sure you have documents in the data/ folder."
        )
    elif isinstance(error, DatabaseCorruptedError):
        return (
            "❌ Vector database appears to be corrupted.\n"
            "💡 Try recreating it by running 'python src/main.py' again."
        )
    elif isinstance(error, QueryEmbeddingError):
        return (
            "❌ Failed to process your query.\n"
            "💡 Check your OpenAI API key and internet connection."
        )
    else:
        return f"❌ An unexpected error occurred: {error}"