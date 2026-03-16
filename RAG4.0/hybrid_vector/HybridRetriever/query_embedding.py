from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-mpnet-base-v2')

def embed_query(query):
    return model.encode([query]).astype('float32')
