def ocr_confidence(ocr_data):
    if len(ocr_data) == 0:
        return 0.0
    
    total = sum([box['text'] for box in ocr_data])

    return total / len(ocr_data)