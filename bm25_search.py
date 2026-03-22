import pickle

def bm25_search(query, doc_id, top_k=5):
    bm25 = pickle.load(open(f"rag_db/documents/{doc_id}/bm25.pkl", "rb"))
    metadata = pickle.load(open(f"rag_db/documents/{doc_id}/metadata.pkl", "rb"))
    
    tokenized_query = query.split()
    scores = bm25.get_scores(tokenized_query)
    top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]
    
    
    results = []
    for i in top_indices:
        results.append({
            "chunk_text": metadata[i]["chunk_text"],
            "score": scores[i]
        })
    
    return results

