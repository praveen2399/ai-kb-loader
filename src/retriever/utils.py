"""
Utilities for ChromaDB vector retrieval system including validation and error handling.
"""

import os
import json
from typing import Optional, Dict, Any, Tuple
import logging

logger = logging.getLogger(__name__)


# Custom Exceptions
class DatabaseNotFoundError(Exception):
    """Raised when vector database files are not found."""
    pass


class DatabaseCorruptedError(Exception):
    """Raised when vector database files are corrupted or invalid."""
    pass


class QueryEmbeddingError(Exception):
    """Raised when query embedding fails."""
    pass


def validate_search_params(query: str, top_k: int) -> None:
    """
    Validate search parameters.
    
    Args:
        query: Search query
        top_k: Number of results to return
        
    Raises:
        ValueError: If parameters are invalid
    """
    if not query or not query.strip():
        raise ValueError("Query cannot be empty")
    
    if len(query.strip()) < 3:
        logger.warning("Very short queries may not return relevant results")
    
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
