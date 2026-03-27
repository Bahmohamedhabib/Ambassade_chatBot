import pytest
from app.rag.chunker import DocumentChunker

def test_document_chunker():
    chunker = DocumentChunker(chunk_size=100, chunk_overlap=20)
    
    mock_pages = [
        {
            "content": "Ceci est un texte de test. Il est suffisamment long pour être découpé en plusieurs morceaux distincts afin de tester la logique du chunker.",
            "metadata": {"source": "test.pdf", "page": 1}
        }
    ]
    
    chunks = chunker.chunk_documents(mock_pages)
    
    assert len(chunks) > 1
    assert "Ceci est un texte" in chunks[0]["content"]
    assert chunks[0]["metadata"]["source"] == "test.pdf"
    assert chunks[0]["metadata"]["page"] == 1
    assert "chunk_index" in chunks[0]["metadata"]
