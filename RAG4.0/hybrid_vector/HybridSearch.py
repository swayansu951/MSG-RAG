from HybridRetriever.ChunkRetriever import ChunkRetriever
from bm25_search import bm25_search

def hybrid_search(query, doc_id, top_k=5):
    vector_retriever = ChunkRetriever(doc_id)

    vector_result = vector_retriever.retrieve_chunks(query, doc_id)
    bm25_result = bm25_search(query, doc_id)

    candidate= []
    for r in vector_result:
        candidate.append(r["chunk_text"])
    
    for r in bm25_result:
        candidate.append(r["chunk_text"])

    candidate = list(set(candidate))

    return candidate