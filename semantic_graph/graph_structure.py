class Node: 
    def __init__(self, id, type, value):
        self.id = id
        self.type = type
        self.value = value
        self.edges = []
        self.confidence = 0.0
        
class Edge:
    def __init__(self, src, dst, type, confidence = 1.0):
        self.src = src
        self.dst = dst
        self.type = type
        self.confidence = confidence

attribute_nodes = {}

class Graph:
    def __init__(self):
        self.nodes = {}
        self.edges = []

    def add_node(self, node):
        if node.id not in self.nodes:
            self.nodes[node.id] = node
    
    def add_edge(self, edge):
        if edge not in self.edges:
            self.edges.append(edge)
        if edge.src in self.nodes:
            self.nodes[edge.src].edges.append(edge)
        if edge.dst in self.nodes:
            self.nodes[edge.dst].edges.append(edge)

def extract_attribute(header_row):
    return [h.strip().lower() for h in header_row]


def detect_type(value):
    v = value.replace(",", "").strip()
    try:
        float(v)
        return "number" 
    except Exception as e:
        print(f"error : {e}")
    if "%" in value:
        return "percentage"
    if any(sym in value for sym in ["$", "₹", "€", "£"]):
        return "currency"
    return "text"

def table_to_graph(table):
    graph = Graph()
    
    header = table[0]
    attribute = extract_attribute(header)
    entities = []

    table_node = Node("table_1", "table", "employee Data")
    graph.add_node(table_node)

    for row in table[1:]:
        entity_value = row[0]

        entity_node = Node(f"entity_{entity_value}", "entity", entity_value)
        graph.add_node(entity_node)
        entities.append(entity_node)
        graph.add_edge(Edge(entity_node.id, table_node.id, "belongs_to"))   

        for attr, val in zip(attribute[1:], row[1:]):
            attr_id = f"attr_{attr}"
            if f"attr_{attr}" not in graph.nodes:
                attr_node = Node(f"attr_{attr}", "attribute", attr)
            if attr_id not in graph.nodes:
                graph.add_node(Node(attr_node.id, "attribute", attr))
            val_id = f"value_{val}_{attr}"
            val_node = Node(f"value_{val}", detect_type(val), val)

            # graph.add_node(attribute_nodes[attr])
            graph.add_node(val_node)

            graph.add_edge(Edge(entity_node.id, attr_node.id, "has_attribute"))
            graph.add_edge(Edge(attr_node.id, val_node.id, "has_value"))
            graph.add_edge(Edge(entity_node.id, val_node.id, "has_value_direct"))
    
    return graph

def node_confidence(node):
    if not node.edges:
        return 0.0
    
    weighted_sum = 0
    total_weight = 0
    
    for edge in node.edges:
        weight = 1.0

        if edge.type == "has_value":
            weight = 1.2
        elif edge.type == "has_value_direct":
            weight = 1.5
        elif edge.type == "has_attribute":
            weight = 1.0
        elif edge.type == "temporal":
            weight = 0.8
        
        weighted_sum += edge.confidence * weight
        total_weight += weight

    return weighted_sum / total_weight

def update_all_node_confidences(graph):
    for node in graph.nodes.values():
        node.confidence = node_confidence(node)

# example of use
# graph = table_to_graph(table)
# update_all_node_confidences(graph)