from pipeline import DocumentProcessor

def run_system(image, ocr_data, query):
    process = DocumentProcessor()
    result = process.process(image, ocr_data, query)

    print("Route : ", result["router"])
    print("Signals : ", result["signals"])
    print("Answer : ", result['result'])
    
    return result