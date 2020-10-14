import networkx as nx
from typing import List, Tuple


def _create_graph(matches: List[Tuple[int, int, float]]) -> nx.Graph:
    G = nx.Graph()

    # Add the nodes
    source_nodes = []
    target_notes = []
    source_index_to_node = {}
    target_index_to_node = {}
    source_node_to_index = {}
    target_node_to_index = {}
    count = 1
    for i, j, _ in matches:
        if i not in source_index_to_node:
            source_nodes.append(count)
            source_index_to_node[i] = count
            source_node_to_index[count] = i
            count += 1
        if j not in target_index_to_node:
            target_notes.append(count)
            target_index_to_node[j] = count
            target_node_to_index[count] = j
            count += 1

    G.add_nodes_from(source_nodes, bipartite=0)
    G.add_nodes_from(target_notes, bipartite=1)

    # Add the edges
    for i, j, weight in matches:
        source = source_index_to_node[i]
        target = target_index_to_node[j]
        G.add_edge(source, target, weight=weight)

    return G


def calculate_maximum_matching(matches: List[Tuple[int, int, float]]) -> float:
    if len(matches) == 0:
        return 0.0

    G = _create_graph(matches)

    # Compute the matching and convert the node ids back to the indices
    matching = nx.algorithms.matching.max_weight_matching(G)
    weight = 0
    for i, j in matching:
        weight += G[i][j]['weight']
    return weight