import networkx as nx
import scipy as sp
import random

N = 50
index = 0

name_nodes = list(range(1, N + 1))
G = nx.DiGraph()

G.add_node(name_nodes[index])
index += 1
pivot = 0


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

a = nx.adjacency_matrix(G)
print(a.todense())
