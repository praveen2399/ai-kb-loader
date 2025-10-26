import os
import numpy as np
from openai import OpenAI
from tqdm import tqdm
import time

client = OpenAI()

def embed_documents(chunks, batch_size=100):
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not set.")

    ids = [f"chunk_{i}" for i in range(len(chunks))]
    vectors = []
    
    print(f"Processing {len(chunks)} chunks in batches of {batch_size}")
    
    # Process chunks in batches
    for i in tqdm(range(0, len(chunks), batch_size), desc="Generating embeddings"):
        batch = chunks[i:i+batch_size]
        
        try:
            # Batch API call - much faster than individual calls
            response = client.embeddings.create(
                model="text-embedding-3-small", 
                input=batch
            )
            
            # Extract embeddings from batch response
            batch_vectors = [data.embedding for data in response.data]
            vectors.extend(batch_vectors)
            
            # Small delay to respect rate limits
            if i + batch_size < len(chunks):
                time.sleep(0.1)
                
        except Exception as e:
            print(f"Error processing batch {i//batch_size + 1}: {e}")
            # Retry with smaller batch or individual calls if needed
            for chunk in batch:
                try:
                    response = client.embeddings.create(
                        model="text-embedding-3-small", 
                        input=chunk
                    )
                    vectors.append(response.data[0].embedding)
                    time.sleep(0.2)  # Longer delay for individual calls
                except Exception as chunk_error:
                    print(f"Failed to embed chunk: {chunk_error}")
                    # Use zero vector as fallback
                    vectors.append([0.0] * 1536)  # text-embedding-3-small dimension

    return np.array(vectors), ids


def embed_single_text(text: str) -> np.ndarray:
    """
    Embed a single text string. Useful for query embedding.
    
    Args:
        text: The text to embed
        
    Returns:
        numpy array of the embedding vector
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not set.")
    
    try:
        response = client.embeddings.create(
            model="text-embedding-3-small", 
            input=text
        )
        return np.array(response.data[0].embedding)
        
    except Exception as e:
        print(f"Error embedding text: {e}")
        # Return zero vector as fallback
        return np.array([0.0] * 1536)


def embed_query(query: str) -> np.ndarray:
    """
    Alias for embed_single_text for query embedding.
    
    Args:
        query: The query string to embed
        
    Returns:
        numpy array of the query embedding
    """
    return embed_single_text(query)
