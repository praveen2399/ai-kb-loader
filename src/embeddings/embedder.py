import os
import numpy as np
from openai import OpenAI

client = OpenAI()

def embed_documents(chunks):
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not set.")

    ids = [f"chunk_{i}" for i in range(len(chunks))]
    vectors = []

    for chunk in chunks:
        response = client.embeddings.create(model="text-embedding-3-small", input=chunk)
        vectors.append(response.data[0].embedding)

    return np.array(vectors), ids
