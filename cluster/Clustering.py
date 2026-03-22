from ingestion.signals.alignment import cluster_position

def cluster_rows(ocr_data, y_threshold = 15):
    ocr_data = sorted(ocr_data, key = lambda x : x['y'])
    
    rows = []

    current_row = [ocr_data[0]]

    for box in ocr_data[1:]:
        if abs(box['y'] - current_row[-1]['y'] < y_threshold):
            current_row.append(box)

        else:
            rows.append(current_row)
            current_row = [box]
    
    rows.append(current_row)
    
    return rows

def extraction_column_position(rows):
    x_position = []

    for row in rows:
        for box in row:
            x_position.append(box['x'])

    return cluster_position(x_position, threshold=20)

def assign_columns(rows, column_clusters):
    table = []

    col_centers = [sum(c)/len(c) for c in column_clusters]

    for row in rows:
        table_row = [""] * len(col_centers)

        for box in row:
            distance = [abs(box['x'] - c) for c in col_centers]
            col_idx = distance.index(min(distance))

            table_row[col_idx] = box['text']
        
        table.append(table_row)
    
    return table

def fill_missing_cells(table):
    return table

def header_detect(table):
    first_row = table[0]

    score = sum(len(cell) for cell in first_row)

    if score > 5:
        return first_row, table[1:]
    
    return None, table

def reconstruct_table(ocr_data):
    rows = cluster_rows(ocr_data)

    column_clusters = extraction_column_position(rows)

    table = assign_columns(rows, column_clusters)

    table = fill_missing_cells(table)

    header, body = header_detect(table)

    return {
        "header" : header,
        "body" : body
    }