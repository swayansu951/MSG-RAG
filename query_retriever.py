from semantic_graph.graph_structure import node_confidence
from ingestion.graph_storage import load_graphs
# query retrieve for graph retrieval (table understanding)
def normalize(text):
    return text.lower().strip()

def score_match(text, query_words):
    words = text.split()
    return  sum(1 for w in query_words if w in words)

def find_best_entity(graph, query):
    query_words = normalize(query).split()

    best_node = None
    best_score = 0
    
    for node in graph.nodes.values():
        if node.type != "entity":
            continue

        name = normalize(node.value)

        score = score_match(name, query_words)

        if score > best_score:
            best_score = score
            best_node = node
        
    return best_node, best_score

def get_value_from_entity(entity_node, attr_node, graph):
    for edge in entity_node.edges:
        if edge.type == "has_value_direct":
            value_node = graph.nodes[edge.dst]

            for e in graph.edges:
                if e.src == attr_node.id and e.dst == value_node.id:
                    return value_node
    return None

def find_best_attribute(graph, query):
    query_words = normalize(query).split()

    best_attr = None
    best_score = 0

    for node in graph.nodes.values():
        if node.type != "attribute":
            continue

        attr = normalize(node.value)

        score = score_match(attr, query_words)

        if score > best_score:
            best_score = score
            best_attr = node

    return best_attr, best_score

def find_attribute_node(entity_node, attribute_node):
    for edge in entity_node.edges:
        if edge.type == "has_attribute" and edge.dst == attribute_node.id:
            return attribute_node
    return None

def get_value_node(entity_node, graph, attr_node):
    for edge in entity_node.edges:
        if edge.dst == attr_node.id and edge.type == "has_attribute":
            for e in graph.edges:
                if e.src == attr_node.id and e.type == "has_value":
                    return graph.nodes[edge.dst]
    return None

def answer_query(graph, query):
    entity_node, entity_score = find_best_entity(graph, query)
    attr_node, attr_score = find_best_attribute(graph, query)

    if not entity_node:
        return "[-] Entity not found", 0.0
    
    if not attr_node:
        return "[-] Attribute not found", 0.0
    
    attr_match = find_attribute_node(entity_node, attr_node)

    if not attr_match:
        return "[-] No relation found", 0.0
    
    value_node = get_value_node(graph, attr_match)

    if not value_node:
        return "[-] Value not found", 0.0
    
    node_conf = node_confidence(value_node)

    len_q = len(query.split())

    final_conf = (
        0.5 * node_conf + 
        0.25 * (entity_score / len_q) +
        0.25 * (attr_score / len_q)
    )

    return value_node.value, round(final_conf, 3)

def graph_query_engine(query, doc_id):
    graphs = load_graphs(doc_id)

    best_answer = None
    best_conf = 0.0

    for graph in graphs:
        answer, conf = answer_query(graph, query)

        if conf > best_conf:
            best_conf = conf
            best_answer = answer

    return best_answer, best_conf