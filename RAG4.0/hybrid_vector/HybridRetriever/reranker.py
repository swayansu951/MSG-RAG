from sentence_transformers import CrossEncoder
import torch

reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2', device="cuda") if torch.cuda.is_available() else CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2', device="cpu")

def rerank(query, chunks, top_k=5):
    
    pairs = [[query, chunk] for chunk in chunks]
    scores = reranker.predict(pairs)
    scored_chunks = list(zip(chunks, scores))
    
    scored_chunks.sort(key=lambda x: x[1], reverse=True)
    
    return [chunk for chunk, score in scored_chunks[:top_k]]