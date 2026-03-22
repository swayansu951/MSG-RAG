import ollama
import re
from HybridSearch import hybrid_search
from HybridRetriever.reranker import rerank
from context_builder import build_context
from database.ingest_pdf import ingest_pdf
import os
from query_retriever import graph_query_engine

class GENERATE:
    prompt = f"""
            Answer the question using the context below. If the answer is not found in the context, say "I don't know".
            Context:
            {"context"}
            Question:
            {"user_input"}
            """
    def __init__(self):
        self.messages = [{'role': 'system', 'content': self.prompt}]

    def retrieve_context(self, query, doc_id):
        # text retrieval
        candidates = hybrid_search(query,doc_id)
        reranked = rerank(query, candidates)
        context = build_context(reranked)
        # graph retrieval
        graph_answer, graph_conf = graph_query_engine(query, doc_id)

        context = f"""
        TEXT CONTEXT :
        {context}

        TABLE INSIGHT :
        ANSWER : {graph_answer} (confidence : {graph_conf})
        CONFIDENCE : {graph_conf}
        """
        return context

    def generate(self, user_input:str,doc_id):

        context = self.retrieve_context(user_input,doc_id)

        prompt = f"""
        Answer the question using the context below. 
        If the answer is not found in the context, say "I don't know".
        Context:
        {context}
        Question:
        {user_input}
        """
        self.messages = [{"role" : "system" , "context" : prompt}]

        response = ollama.chat(model='llama3.1:8b-instruct-q5_K_S', messages=self.messages, stream=True, options={"num_thread":10,"keep_alive":"1m"})
        full_response = ""
        sentence_buffer = ""

        for chunk in response:
            content = chunk['message']['content']
            full_response += content
            sentence_buffer += content

            if any(p in content for p in [".","!","?","*","\n"]):
                    text_to_speak = re.sub(r'\[.*?\]', '', sentence_buffer).strip()

                    if text_to_speak:
                        yield str(text_to_speak)
                    sentence_buffer= ""

        if sentence_buffer.strip():
                final_text = re.sub(r'\[.*?\]', '', sentence_buffer).strip()
                if final_text:
                    yield final_text

def main():
    rag = GENERATE()
   
    files=[]
    if not os.path.exists("rag_db"):
        os.makedirs("rag_db", exist_ok=True)

    doc_id = None

    
    user = input("\nWant to add file?(yes/no): ").strip()
    
    if "yes" in user:
        pdf = input("\nEnter PDF file with .pdf extension: ").strip()
        if pdf.endswith(".pdf"):
            doc_id = os.path.splitext(pdf)[0]
            ingest_pdf(pdf, doc_id)
            print(f"[+] PDF {pdf} indexed successfully.")
        else:
                print("[-] Invalid PDF file.")
    elif "no" in user:
        if not os.listdir("rag_db/documents"):
                print("[-] No documents found in dataset")
        doc_id = input("\nEnter the document id to use: ")

    while True:
        try:
            text = input("\nEnter your question(else 'bye' to exit): ").strip()

            if "bye" in text:
                break
            for token in rag.generate(text, doc_id):
                print(f"\nResearcher: ", token, end="", flush=True)
        
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()
    