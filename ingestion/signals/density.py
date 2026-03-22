def density_score(ocr_data, image):
    text_area = sum([box['w'] * box['h'] for box in ocr_data])
    total_area = image.shape[0] * image.shape[1]

    density = text_area / total_area

    return min(1.0, density*5)