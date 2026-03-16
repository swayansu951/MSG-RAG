from rank_bm25 import BM25Okapi
import pickle
import os
import faiss
import numpy as np
from database.pdf_loader import load_pdf
from database.summarizer import summarize_document, summarize_chunks
from database.embedding_model import model
from database.chunker import chunk_text

def create_summary_index(dim=384):
    index_path = "rag_db/summary_index.faiss"
    if os.path.exists(index_path):
        print("Loading existing summary index...")
        index = faiss.read_index(index_path)
    else:
        print("Creating new summary index...")
        index = faiss.IndexFlatL2(dim)

    return index

def ingest_pdf(pdf_path, doc_id):
    
    text = load_pdf(pdf_path)
    
    doc_summary = summarize_document(text)
    doc_embedding = model.encode([doc_summary]).astype('float32')
    dim = doc_embedding.shape[1]

    summary_index = create_summary_index(dim)
    summary_index.add(doc_embedding)
    faiss.write_index(summary_index, "rag_db/summary_index.faiss")

    doc_folder = f"rag_db/documents/{doc_id}"
    os.makedirs(doc_folder, exist_ok=True)

    chunks = chunk_text(text)
    chunk_summaries = summarize_chunks(chunks)
    chunk_summary_embeddings = model.encode(chunk_summaries).astype('float32')
    chunk_embeddings = model.encode(chunks).astype('float32')

    chunk_summary_index = faiss.IndexHNSWFlat(dim, 32)
    chunk_index = faiss.IndexHNSWFlat(dim, 32)

    chunk_summary_index.add(chunk_summary_embeddings)
    chunk_index.add(chunk_embeddings)

    faiss.write_index(chunk_summary_index, f"{doc_folder}/chunk_summary_index.faiss")
    faiss.write_index(chunk_index, f"{doc_folder}/chunk_index.faiss")

    tokenized_chunks = [chunk.split() for chunk in chunks]
    bm25 = BM25Okapi(tokenized_chunks)
    pickle.dump(bm25, open(f"{doc_folder}/bm25.pkl", "wb"))

    metadata = {}

    for i,chunk in enumerate(chunks):
        metadata[i] = {
            "chunk_text": chunk,
            "chunk_summary": chunk_summaries[i]
        }
    
    pickle.dump(metadata, open(f"{doc_folder}/metadata.pkl", "wb"))