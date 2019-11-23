import networkx as nx
import scipy as sp
import random
import matplotlib.pyplot as plt
from input_generator import save_input_to_file

N = 100
NUM_TAS = 50
index = 0

name_nodes = list(range(N))
houses = []
def initialize_graph():
    G = nx.DiGraph()
    index = 0
    G.add_node(name_nodes[index])
    index = 1
    pivot = 0
    return G, pivot, index

def add_hourglass(G, pivot, index):
    G.add_nodes_from(name_nodes[index:index+5])

    for i in range(1, 5):
        G.add_edge(index, index + i, weight=100)
        G.add_edge(index + i, index, weight=100)
        houses.append(index + i)

    G.add_edge(index + 1, index + 2, weight=1)
    G.add_edge(index + 2, index + 1, weight=1)

    G.add_edge(index + 3, index + 4, weight=1)
    G.add_edge(index + 4, index + 3, weight=1)

    index += 5
    pivot += 5
    return pivot, index

def add_walk_home(G, pivot, index):
    G.add_nodes_from(name_nodes[index:index+5])

    for i in range(1, 5):
        G.add_edge(index, index + i, weight=2)
        G.add_edge(index + i, index, weight=2)
        houses.append(index + i)

    G.add_edge(index + 1, index + 2, weight=3)
    G.add_edge(index + 2, index + 1, weight=3)

    G.add_edge(index + 3, index + 4, weight=3)
    G.add_edge(index + 4, index + 3, weight=3)

    index += 5
    pivot += 5
    return pivot, index

G, pivot, index = initialize_graph()
for i in range(6):
    pivot, index = add_hourglass(G, pivot, index)
    pivot, index = add_hourglass(G, pivot, index)
    pivot, index = add_walk_home(G, pivot, index)

G.add_edge(0, 1, weight=1)
G.add_edge(1, 0, weight=1)
# G.add_edge(1, 6, weight=1)
# G.add_edge(6, 11, weight=1)
f = 1
while f < index:
    G.add_edge(f, f+5, weight=1)
    G.add_edge(f+5, f, weight=1)
    f += 5

# G.add_nodes_from([97, 98, 99])

# G.add_edge(97, 98, weight=1)
# G.add_edge(98, 97, weight=1)
# G.add_edge(98, 99, weight=1)
# G.add_edge(99, 98, weight=1)
# G.add_edge(0, 99, weight=1)
# G.add_edge(99, 0, weight=1)

# Leftover edges not in hourglass
G.add_nodes_from(list(range(92, 100)))
for i in range(92, 99):
    G.add_edge(i, i+1, weight=1)
    G.add_edge(i+1, i, weight=1)

G.add_edge(0, 99, weight=1)
G.add_edge(99, 0, weight=1)

# Set all 0s to x's
a = nx.adjacency_matrix(G)
matrix = a.toarray().tolist()
for i in range(len(matrix)):
    for j in range(i):
        if matrix[i][j] == 0:
            matrix[i][j] = 'x'
            matrix[j][i] = 'x'

for i in range(len(matrix)):
    matrix[i][i] = 'x'

print(matrix)
print(len(matrix))
print(houses)

houses = houses[-NUM_TAS:]

name_nodes = [str(i) for i in name_nodes]
houses = [str(i) for i in houses]

save_input_to_file(N, N, len(houses), name_nodes, houses, '0', matrix)

# nx.draw(G, with_labels=True)
# plt.show()
