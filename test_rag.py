import sys
import os
from app.rag.vector_store import VectorStore
from app.services.mistral_client import MistralChatClient
from app.rag.retriever import Retriever

store = VectorStore(index_path='data/index/faiss_index.pkl')
retriever = Retriever(store)
client = MistralChatClient()

query = 'je veux connaitre les procedure de renouvellement du passport'
context, sources = retriever.retrieve_context(query)
sources_found = len(sources) > 0

print(f"Sources found: {sources_found} ({len(sources)} chunks)")
print("Context snippets preview:")
for i, s in enumerate(sources):
    print(f"[{i}] {s['content'][:100]}...")

response = client.generate_response(query, context, sources_found)
print("\n=== LLM Response ===")
print(response)
