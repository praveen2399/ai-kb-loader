""""""

Utilities for ChromaDB vector retrieval system including validation and error handling.Utilities for vector retrieval system including validation and error handling.

""""""



import osimport os

import jsonimport json

from typing import Optional, Dict, Any, Tupleimport faiss

import loggingfrom typing import Optional, Dict, Any

import logging

logger = logging.getLogger(__name__)

logger = logging.getLogger(__name__)



# Custom Exceptions

class DatabaseNotFoundError(Exception):class VectorDBValidator:

    """Raised when vector database files are not found."""    """Validator for vector database integrity and consistency."""

    pass    

    @staticmethod

    def validate_files(index_path: str, metadata_path: str) -> Dict[str, Any]:

class DatabaseCorruptedError(Exception):        """

    """Raised when vector database files are corrupted or invalid."""        Validate that required files exist and are accessible.

    pass        

        Args:

            index_path: Path to FAISS index file

class QueryEmbeddingError(Exception):            metadata_path: Path to metadata JSON file

    """Raised when query embedding fails."""            

    pass        Returns:

            Dictionary with validation results

        """

def validate_search_params(query: str, top_k: int) -> None:        validation = {

    """            'valid': True,

    Validate search parameters.            'errors': [],

                'warnings': [],

    Args:            'index_exists': False,

        query: Search query string            'metadata_exists': False,

        top_k: Number of results to return            'index_readable': False,

                    'metadata_readable': False

    Raises:        }

        ValueError: If parameters are invalid        

    """        # Check if index file exists

    if not query or not query.strip():        if os.path.exists(index_path):

        raise ValueError("Query cannot be empty")            validation['index_exists'] = True

                try:

    if not isinstance(top_k, int) or top_k <= 0:                # Try to read the index

        raise ValueError(f"top_k must be a positive integer, got: {top_k}")                faiss.read_index(index_path)

                    validation['index_readable'] = True

    if top_k > 100:            except Exception as e:

        logger.warning(f"Large top_k value ({top_k}) may impact performance")                validation['errors'].append(f"Index file corrupted: {e}")

                validation['valid'] = False

        else:

def format_error_message(error: Exception) -> str:            validation['errors'].append(f"Index file not found: {index_path}")

    """            validation['valid'] = False

    Format error messages for consistent display.        

            # Check if metadata file exists

    Args:        if os.path.exists(metadata_path):

        error: Exception to format            validation['metadata_exists'] = True

                    try:

    Returns:                # Try to read the metadata

        Formatted error message string                with open(metadata_path, 'r', encoding='utf-8') as f:

    """                    json.load(f)

    error_type = type(error).__name__                validation['metadata_readable'] = True

                except Exception as e:

    if isinstance(error, DatabaseNotFoundError):                validation['errors'].append(f"Metadata file corrupted: {e}")

        return f"❌ Database Error: {error}\n💡 Make sure to run 'python src/main.py' to create the database"                validation['valid'] = False

    elif isinstance(error, DatabaseCorruptedError):        else:

        return f"❌ Database Corruption: {error}\n💡 Try recreating the database with 'python src/main.py'"            validation['errors'].append(f"Metadata file not found: {metadata_path}")

    elif isinstance(error, QueryEmbeddingError):            validation['valid'] = False

        return f"❌ Query Processing Error: {error}\n💡 Check your OpenAI API key and internet connection"        

    else:        return validation

        return f"❌ {error_type}: {error}"    

    @staticmethod

    def validate_consistency(index_path: str, metadata_path: str) -> Dict[str, Any]:

def safe_load_database(persist_directory: str, metadata_path: str) -> Tuple[Any, Dict]:        """

    """        Validate consistency between FAISS index and metadata.

    Safely load ChromaDB database with comprehensive validation.        

            Args:

    Args:            index_path: Path to FAISS index file

        persist_directory: Path to ChromaDB persistence directory            metadata_path: Path to metadata JSON file

        metadata_path: Path to metadata JSON file            

                Returns:

    Returns:            Dictionary with consistency validation results

        Tuple of (indexer, metadata)        """

                validation = {

    Raises:            'consistent': True,

        DatabaseNotFoundError: If required files don't exist            'errors': [],

        DatabaseCorruptedError: If files exist but are corrupted            'warnings': [],

    """            'index_count': 0,

    # Import here to avoid circular imports            'metadata_count': 0

    from vectorstore.chroma_indexer import load_from_chroma        }

            

    # Check if ChromaDB directory exists        try:

    if not os.path.exists(persist_directory):            # Load index and get vector count

        raise DatabaseNotFoundError(f"ChromaDB directory not found: {persist_directory}")            index = faiss.read_index(index_path)

                validation['index_count'] = index.ntotal

    # Load metadata            

    metadata = {}            # Load metadata and get count

    if os.path.exists(metadata_path):            with open(metadata_path, 'r', encoding='utf-8') as f:

        try:                metadata_content = json.load(f)

            with open(metadata_path, 'r') as f:                metadata_list = metadata_content.get('metadata', [])

                metadata = json.load(f)                validation['metadata_count'] = len(metadata_list)

        except (json.JSONDecodeError, IOError) as e:            

            raise DatabaseCorruptedError(f"Cannot read metadata file: {e}")            # Check if counts match

    else:            if validation['index_count'] != validation['metadata_count']:

        logger.warning(f"Metadata file not found: {metadata_path}")                validation['consistent'] = False

                    validation['errors'].append(

    # Load ChromaDB                    f"Mismatch: {validation['index_count']} vectors vs {validation['metadata_count']} metadata entries"

    try:                )

        indexer = load_from_chroma(persist_directory)            

                    # Check vector dimension

        # Validate that collection has documents            if index.d != 1536:  # text-embedding-3-small dimension

        stats = indexer.get_collection_stats()                validation['warnings'].append(

        if stats.get("total_documents", 0) == 0:                    f"Unexpected vector dimension: {index.d} (expected 1536)"

            raise DatabaseCorruptedError("ChromaDB collection is empty")                )

                        

        logger.info(f"Successfully loaded database with {stats.get('total_documents', 0)} documents")        except Exception as e:

        return indexer, metadata            validation['consistent'] = False

                    validation['errors'].append(f"Error during consistency check: {e}")

    except Exception as e:        

        if "not found" in str(e).lower():        return validation

            raise DatabaseNotFoundError(f"ChromaDB collection not found: {e}")    

        else:    @staticmethod

            raise DatabaseCorruptedError(f"Cannot load ChromaDB: {e}")    def validate_query(query: str) -> Dict[str, Any]:

        """

        Validate search query input.

def validate_chroma_database(persist_directory: str, metadata_path: str) -> Dict[str, Any]:        

    """        Args:

    Validate ChromaDB database integrity.            query: Query string to validate

                

    Args:        Returns:

        persist_directory: Path to ChromaDB persistence directory            Dictionary with query validation results

        metadata_path: Path to metadata JSON file        """

                validation = {

    Returns:            'valid': True,

        Dictionary with validation results            'errors': [],

    """            'warnings': []

    validation = {        }

        'valid': True,        

        'errors': [],        if not query or not query.strip():

        'warnings': [],            validation['valid'] = False

        'directory_exists': False,            validation['errors'].append("Query cannot be empty")

        'metadata_exists': False,            return validation

        'collection_accessible': False,        

        'document_count': 0        # Check query length

    }        if len(query.strip()) < 3:

                validation['warnings'].append("Very short queries may not return relevant results")

    # Check if ChromaDB directory exists        

    if os.path.exists(persist_directory):        if len(query) > 5000:

        validation['directory_exists'] = True            validation['warnings'].append("Very long queries may be truncated")

    else:        

        validation['errors'].append(f"ChromaDB directory not found: {persist_directory}")        return validation

        validation['valid'] = False

        return validation

    class RetrieverError(Exception):

    # Check metadata file    """Custom exception for retrieval system errors."""

    if os.path.exists(metadata_path):    pass

        validation['metadata_exists'] = True

        try:

            with open(metadata_path, 'r') as f:class DatabaseNotFoundError(RetrieverError):

                metadata = json.load(f)    """Raised when vector database files are not found."""

                validation['metadata_content'] = metadata    pass

        except Exception as e:

            validation['errors'].append(f"Cannot read metadata: {e}")

            validation['valid'] = Falseclass DatabaseCorruptedError(RetrieverError):

    else:    """Raised when vector database files are corrupted."""

        validation['warnings'].append(f"Metadata file not found: {metadata_path}")    pass

    

    # Try to access ChromaDB collection

    try:class QueryEmbeddingError(RetrieverError):

        from vectorstore.chroma_indexer import load_from_chroma    """Raised when query embedding fails.""" 

        indexer = load_from_chroma(persist_directory)    pass

        validation['collection_accessible'] = True

        

        stats = indexer.get_collection_stats()def safe_load_database(index_path: str, metadata_path: str) -> tuple:

        validation['document_count'] = stats.get('total_documents', 0)    """

            Safely load database with comprehensive error handling.

        if validation['document_count'] == 0:    

            validation['warnings'].append("Database is empty")    Args:

                    index_path: Path to FAISS index

    except Exception as e:        metadata_path: Path to metadata JSON

        validation['errors'].append(f"Cannot access ChromaDB collection: {e}")        

        validation['valid'] = False    Returns:

            Tuple of (index, metadata) or raises appropriate exception

    return validation        

    Raises:

        DatabaseNotFoundError: If files don't exist

def get_database_info(persist_directory: str = "output/chroma_db") -> Dict[str, Any]:        DatabaseCorruptedError: If files are corrupted

    """    """

    Get comprehensive information about the ChromaDB database.    # Validate files exist and are readable

        file_validation = VectorDBValidator.validate_files(index_path, metadata_path)

    Args:    

        persist_directory: Path to ChromaDB persistence directory    if not file_validation['valid']:

                missing_files = []

    Returns:        if not file_validation['index_exists']:

        Dictionary containing database information            missing_files.append(index_path)

    """        if not file_validation['metadata_exists']:

    info = {            missing_files.append(metadata_path)

        'status': 'unknown',        

        'error': None,        if missing_files:

        'stats': {},            raise DatabaseNotFoundError(f"Database files not found: {', '.join(missing_files)}")

        'metadata': {}        else:

    }            raise DatabaseCorruptedError(f"Database files corrupted: {', '.join(file_validation['errors'])}")

        

    try:    # Check consistency

        # Validate database    consistency_validation = VectorDBValidator.validate_consistency(index_path, metadata_path)

        metadata_path = os.path.join(persist_directory, "metadata.json")    

        validation = validate_chroma_database(persist_directory, metadata_path)    if not consistency_validation['consistent']:

                logger.warning(f"Database consistency issues: {', '.join(consistency_validation['errors'])}")

        if not validation['valid']:        # Don't fail on consistency issues, just log warnings

            info['status'] = 'invalid'    

            info['error'] = '; '.join(validation['errors'])    try:

            return info        # Load the files

                index = faiss.read_index(index_path)

        # Load and get stats        

        from vectorstore.chroma_indexer import load_from_chroma        with open(metadata_path, 'r', encoding='utf-8') as f:

        indexer = load_from_chroma(persist_directory)            metadata_content = json.load(f)

        info['stats'] = indexer.get_collection_stats()            metadata = metadata_content.get('metadata', [])

                

        # Load metadata        return index, metadata

        if os.path.exists(metadata_path):        

            with open(metadata_path, 'r') as f:    except Exception as e:

                info['metadata'] = json.load(f)        raise DatabaseCorruptedError(f"Failed to load database: {e}")

        

        info['status'] = 'ready'

        def validate_search_params(query: str, top_k: int) -> None:

    except Exception as e:    """

        info['status'] = 'error'    Validate search parameters.

        info['error'] = str(e)    

        Args:

    return info        query: Search query
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