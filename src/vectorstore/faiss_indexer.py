import faiss
import numpy as np

def save_to_faiss(vectors, ids, output_path="faiss_index.index"):
    dim = len(vectors[0])
    index = faiss.IndexFlatL2(dim)
    index.add(np.array(vectors).astype("float32"))
    faiss.write_index(index, output_path)
    print(f"FAISS index saved at {output_path}")
