import pickle
import os

def save_graphs(graphs, doc_id):
    os.makedirs("rag_db/graphs", exist_ok = True)

    with open(f"rag_db/graphs/{doc_id}.pkl", "wb") as f:
        pickle.dump(graphs, f)

def load_graphs(doc_id):
    path = f"rag_db/graphs/{doc_id}.pkl"

    if not os.path.exists(path):
        return []
    
    with open(path, 'rb') as f:
        return pickle.load(f)