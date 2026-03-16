import faiss
import pickle
from HybridRetriever.query_embedding import embed_query

class ChunkRetriever:
    def __init__(self, doc_id):
        self.index = faiss.read_index(f"rag_db/documents/{doc_id}/chunk_summary_index.faiss")
        self.metadata = pickle.load(open(f"rag_db/documents/{doc_id}/metadata.pkl", "rb"))

    def retrieve_chunks(self,query, doc_id, top_k=5):

        query_embedding = embed_query(query)

        # chunk_summary_index = faiss.read_index(f"rag_db/documents/{doc_id}/chunk_summary_index.faiss")
        chunk_index = faiss.read_index(f"rag_db/documents/{doc_id}/chunk_index.faiss")

        summary_distances, summary_ids = self.index.search(query_embedding, top_k)
        chunk_distances, chunk_ids = chunk_index.search(query_embedding, top_k)

        # metadata = pickle.load(open(f"rag_db/documents/{doc_id}/metadata.pkl", "rb"))
        
        results = []
        
        # for i in summary_ids[0]:
        #     results.append(metadata[i]["chunk_summary"])
        for rank, chunk_id in enumerate(summary_ids[0]):
            
            if chunk_id == -1:
                continue
            chunk_data = self.metadata[chunk_id]

            results.append({
                "chunk_id":chunk_id,
                "chunk_text": chunk_data["chunk_text"],
                "chunk_summary": chunk_data["chunk_summary"],
                "summary_distance": summary_distances[0][rank]
            })

        return results