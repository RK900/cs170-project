import networkx as nx
import scipy as sp
import random
import matplotlib.pyplot as plt

N = 50
index = 0

name_nodes = list(range(1, N + 1))
def initialize_graph():
    G = nx.DiGraph()
    index = 0
    G.add_node(name_nodes[index])
    index = 1
    pivot = 0
    return G, index, pivot

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


    G.add_edge(pivot, pivot+1)
    pivot += 5

G, index, pivot = initialize_graph()
add_hourglass(G, index, pivot)

a = nx.adjacency_matrix(G)
print(a.todense())

nx.draw(G, with_labels=True)
plt.show()
