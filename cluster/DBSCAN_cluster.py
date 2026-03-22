from sklearn.cluster import DBSCAN
import numpy as np

# confidence scorer
def merge_confidence(boxes):
    if not boxes:
        return 0.0
    return sum(b['conf'] for b in boxes) / len(boxes)
# row confidence
def row_confidence(cell_confs):
    if not cell_confs:
        return 0.0
    return sum(cell_confs) / len(cell_confs)
# not to ignore the boxes as dbscan labels some boxes as -1 -> gets ignored
def assign_noise_to_nearest_cluster(ocr_data, labels, axis = 'y'):
    clustered = {}
    noise_points = []

    for box, label in zip(ocr_data, labels):
        if label == -1:
            noise_points.append(box)
        
        else:
            clustered.setdefault(label, []).append(box)
    # compute cluster centers
    centers = {
        label : np.mean([b[axis] for b in boxes])
        for label, boxes in clustered.items()
    }
    # assign noise
    for box in noise_points:
        distances = {l : abs(box[axis] - c) for l, c in centers.items()}
        nearest = min(distances, key = distances.get)
        clustered[nearest].append(box)
    
    return list(clustered.values())
# to hadle same row split into multiple clusters 
def merge_close_rows(rows, threshold = 10):
    merged = []

    rows = sorted(rows, key = lambda r : np.mean([b['y'] for b in r]))

    current = rows[0]

    for r in rows[1:]:
        y_curr = np.mean([b['y'] for b in current])
        y_next = np.mean(b['y'] for b in r)

        if abs(y_curr - y_next) < threshold:
            current.extend(r)
        
        else:
            merged.append(current)
            current = r
    
    merged.append(current)
    
    return merged
# to merged special symbols 
def smart_join(text1, text2):
    if text1.endswith("$") or text1.endswith("₹") or text1.endswith("€") or text1.endswith("£"):
        return text1 + text2
    if text2 in [",", ".", "%"]:
        return text1 + text2
# merge cells in the rows
def merge_cells_in_rows(row, col_centers, x_gap_threshold = 15):
    # group boxes by columnn index
    col_group = {i : [] for i in range(len(col_centers))}

    for box in row:
        cx = box['cx'] 
        distances = [abs(cx - c) for c in col_centers]
        col_idx = distances.index(min(distances))
        col_group['col_index'].append(box)
    
    merged_row = []
    confidences = []
    
    for col_idx in sorted(col_group.keys()):
        boxes = col_group[col_idx]

        if not boxes:
            merged_row.append("")
            confidences.append(0.0)
            continue

        boxes = sorted(boxes, key=lambda b:b['x'])
        merged_text = boxes[0]['text']
        merged_text = smart_join(merged_text, box['text'])
        prev_box = boxes[0]
    
    for box in boxes[1:]:
        gap = box['x'] - (prev_box['x'] + prev_box['w'])

        if gap < x_gap_threshold:
            merged_text += " " + box['text']

        else:
            merged_text += "|" + box['text']

        prev_box = box
    conf = merge_confidence(boxes)

    merged_row.append(merged_text)
    confidences.append(conf)

    return merged_row
# merging vertically
def merge_vertical_fragments(rows, col_centers, y_threshold = 10):
    for col_idx in range(len(col_centers)):
        prev_text = None

        for i in range(len(rows)):
            cell = rows[i][col_idx]

            if not cell:
                continue

            if prev_text is None:
                prev_text = cell
            else:
                rows[i][col_idx] = prev_text + " " + cell
                rows[i-1][col_idx] = ""
                prev_text = rows[i][col_idx]

    return rows 
# normalize the coordinates
def normalize_coordinates(ocr_data):
    # use center instead of top-left
    for box in ocr_data:
        box['cx'] = box['x'] + box['w'] / 2
        box['cy'] = box['y'] + box['h'] / 2

    return ocr_data
# sparse rows / handle missing cells
def normalize_table(table):
    max_cols = max(len(row) for row in table)

    normalized = []
    for row in table:
        if len(row) < max_cols:
            row += [""] * (max_cols - len(row))
        normalized.append(row)

    return normalized
# snap columns to global centers
def refine_column_centers(col_center, threshold = 15):
    refined = []

    for c in sorted(col_center):
        if not refined:
            refined.append(c)
        elif abs(c - refined[-1]) < threshold:
            refined[-1] = (refined[-1] + c)/2
        else:
            refined.append(c)

    return refined
# filter noisy text before clustering
def filter_noise(ocr_data):
    filtered = []

    for box in ocr_data:
        if box['conf'] < 0.5:
            continue
        if len(box['text'].strip()) == 0:
            continue
        if box['w'] < 5 or box['h'] < 5:
            continue
        filtered.append(box)
    
    return filtered
# dynamic eps estimator
def eps_estimate(ocr_data, axis='y'):
    
    coords = sorted(box[axis] for box in ocr_data)

    diffs = [coords[i+1] - coords[i] for i in range(len(coords) - 1)]

    if len(diffs) == 0:
        return 10
    
    return np.median(diffs) * 1.5

def cluster_rows_dbscan(ocr_data, eps=15, min_samples=1):
    if len(ocr_data) == 0:
        return []
    
    y_coords = np.array([[box['y']] for box in ocr_data])

    clustering = DBSCAN(eps=eps, min_samples=min_samples).fit(y_coords)

    labels = clustering.labels_

    rows = {}

    for label, box in zip(labels, ocr_data):
        if label == -1:
            continue
        rows.setdefault(label, []).append(box)

    sorted_rows = sorted(rows.values(), key=lambda r : np.mean([b['y'] for b in r]))

    return sorted_rows

def cluster_columns_dbscan(ocr_data, eps = 20, min_sample = 1):
    if len(ocr_data) == 0 :
        return []
    
    x_cood = np.array([[box['x']] for box in ocr_data])

    cluster = DBSCAN(eps = eps, min_samples = min_sample).fit(x_cood)

    labels = cluster.labels_

    cols = {}
    for label, box in zip(labels, ocr_data):
        if label == -1:
            continue
        cols.setdefault(labels, []).append(box['x'])

    col_centers = [np.mean(c) for c in cols.values()]

    col_centers.sort()

    return col_centers

def assign_column_with_centers(rows, col_centers):
    table = []

    for row in rows:
        table_row = [""] * len(col_centers)

        for box in row:
            center_x = box['x'] + box['w'] / 2

            distance = [abs(center_x - c) for c in col_centers]
            col_idx = distance.index(min(distance))

            table_row['col_idx'] = box['text']

        table.append(table_row)
    
    return table

def clean_table(table):
    cleaned = []
    for row in table:
        cleaned.append(cell.strip() for cell in row)

    return cleaned

def reconstrucr_with_merging(rows, col_centers):
    table = []

    for row in rows:
        merged_row = merge_cells_in_rows(row, col_centers)
        table.append(merged_row)

    return table

def reconstruct_table(ocr_data):
    ocr_data = filter_noise(ocr_data)
    ocr_data = normalize_coordinates(ocr_data)

    eps_y = eps_estimate(ocr_data, 'cy')
    rows = cluster_rows_dbscan(ocr_data, eps=eps_y)
    
    rows = merge_close_rows(rows)

    all_boxes = [box for row in rows for box in row]
    
    eps_x = eps_estimate(ocr_data , 'cx')
    col_centers = cluster_columns_dbscan(all_boxes, eps = eps_x)
    col_centers = refine_column_centers(col_centers)

    table = reconstrucr_with_merging(rows, col_centers)
    table = merge_vertical_fragments(table, col_centers)
    # table = assign_column_with_centers(rows, col_centers)
    table = normalize_table(table)
    table = clean_table(table)
    
    return table
# table structure confidence counter
def structure_confidence(table):
    total_cells = sum(len(r) for r in table)
    empty_cells = sum(cell == "" for row in table for cell in row)

    sparsity = empty_cells / total_cells

    return max(0.0, 1.0 - sparsity)
# clustering confidence
def clustering_confidence(rows):
    variances = []

    for row in rows:
        ys = [b['cy'] for b in row]
        if len(ys) > 1:
            variances.append(np.var(ys))

    if not variances:
        return 0.0
    
    avg_var = np.mean(variances)

    return max(0.0, 1.0 - avg_var / 100)
# table confidence 
def table_confidence(cell_confs, structure_confs, cluster_confs):
    avg_cell_conf = sum(cell_confs) / len(cell_confs)

    score = (
        0.5 * avg_cell_conf +
        0.3 * structure_confs +
        0.2 * cluster_confs
    )

    edge_conf = (
        cell_confs * structure_confs * cluster_confs
    )
    
    return score