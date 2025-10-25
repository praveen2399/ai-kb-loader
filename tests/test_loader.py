from loader.document_loader import chunk_text

def test_chunk_text():
    text = "This is a test document for chunking purpose."
    chunks = chunk_text(text, size=3)
    assert isinstance(chunks, list)
    assert len(chunks) > 0
