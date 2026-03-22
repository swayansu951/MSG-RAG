import numpy as np

def alignment_score(ocr_data):
    if len(ocr_data) == 0:
        return 0.0
    
    x_position = [box['x'] for box in ocr_data]
    y_position = [box['y'] for box in ocr_data]

    x_cluster = cluster_position(x_position)
    y_cluster = cluster_position(y_position)

    score = min(1.0, (len(x_cluster) + len(y_cluster)) /20.0)

    return score

def cluster_position(values, threshold = 10):
    values = sorted(values)
    cluster = []

    current_cluster = [values[0]]

    for v in values[1:]:
        if abs(v - current_cluster[-1] < threshold):
            current_cluster.append(v)

        else:
            cluster.append(current_cluster)
            current_cluster = [v]
    
    cluster.append(current_cluster)
    
    return cluster