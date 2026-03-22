from collections import Counter

def repetition_score(ocr_data):
    texts = [box['text'] for box in ocr_data]

    patterns = [len(t.split()) for t in texts]

    count = Counter(patterns)

    if len(count) == 0:
        return 0.0
    
    most_common = count.most_common(1)[0][1]
    score = most_common / len(texts)

    return score