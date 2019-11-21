import networkx as nx
from util import *

def build_nx_graph_given_file(input_file):
    # Used adjacency_matrix_to_graph instead of other version to provide names to locations and labels to them
    num_of_locations, num_houses, list_locations, list_houses, starting_car_location, adjacency_matrix = data_parser(
        input_file)
    return build_graph_given(num_of_locations, num_houses, list_locations,
                      list_houses, starting_car_location, adjacency_matrix)

# For optimization of skipping to write to file
def build_graph_given(num_of_locations, num_houses, list_locations, list_houses, starting_car_location, adjacency_matrix):
    G = nx.DiGraph()
    G.add_nodes_from(list_locations)
    for i, loc in enumerate(num_of_locations):
        for j, other_loc in enumerate(num_of_locations):
            if i == j:
                continue
            if adjacency_matrix[i][j] == 'x':
                continue
            G.add_edge(loc, other_loc, weight=adjacency_matrix[i][j])
            G.add_edge(loc, other_loc, weight=adjacency_matrix[i][j])
    return G, list_locations, list_houses, starting_car_location

