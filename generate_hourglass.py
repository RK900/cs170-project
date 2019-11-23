import networkx as nx
import scipy as sp
import random
import matplotlib.pyplot as plt

N = 50
index = 0

name_nodes = list(range( N))
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
        G.add_edge(index, index + i, weight=1)
        G.add_edge(index + i, index, weight=1)

    G.add_edge(index + 1, index + 2, weight=1.5)
    G.add_edge(index + 2, index + 1, weight=1.5)

    G.add_edge(index + 3, index + 4, weight=1.5)
    G.add_edge(index + 4, index + 3, weight=1.5)

    index += 5
    pivot += 5
    return pivot, index

G, pivot, index = initialize_graph()
pivot, index = add_hourglass(G, pivot, index)
pivot, index = add_hourglass(G, pivot, index)
pivot, index = add_walk_home(G, pivot, index)

G.add_edge(0, 1, weight=1)
G.add_edge(1, 0, weight=1)
# G.add_edge(1, 6, weight=1)
# G.add_edge(6, 11, weight=1)

a = nx.adjacency_matrix(G)
a.toarray()
print((a.toarray()))
print(type(a.toarray().tolist()))

print(pivot, index)

nx.draw_shell(G, with_labels=True)
# plt.show()
