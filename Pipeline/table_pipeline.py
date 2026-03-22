from cluster.DBSCAN_cluster import reconstruct_table
from semantic_graph.graph_structure import table_to_graph, node_confidence
from query_retriever import answer_query

def process_table(ocr_data, query):
    table = reconstruct_table(ocr_data)

    graph = table_to_graph(table)

    for node in graph.nodes.values():
        node.confidence = node_confidence(node)

    answer, conf = answer_query(graph, query)

    return {
        "table" : table,
        "answer" : answer,
        "confidence" : conf
    }
