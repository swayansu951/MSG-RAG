import main

def process_text(ocr_data, query):
    text = " ".join([b['text'] for b in ocr_data])

    # TUDO: Integrate RAG4.0

    return {
        "answer" : "RAG answer placeholder",
        "confidence" : 0.7
    }