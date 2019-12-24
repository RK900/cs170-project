"""
A quick script to generate inputs that are hourglass form for the project.
"""
import networkx as nx
import scipy as sp
import random
import matplotlib.pyplot as plt
from input_generator import save_input_to_file

N = 200
NUM_TAS = 100
index = 0

def create_dummy_output(N, list_houses=None):

	with open('outputs/%i.out' % N, 'w') as temp:
		temp.writelines('0' + "\n")
		temp.writelines(str(1) + "\n")
		temp.writelines('0 ' + " ".join(list_houses) + "\n")


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
        r = random.randint(-10, 10)
        G.add_edge(index, index + i, weight=100+r)
        G.add_edge(index + i, index, weight=100+r)
        houses.append(index + i)

    r = random.randint(-9, 9)
    G.add_edge(index + 1, index + 2, weight=20+r)
    G.add_edge(index + 2, index + 1, weight=20+r)

    G.add_edge(index + 3, index + 4, weight=20+r)
    G.add_edge(index + 4, index + 3, weight=20+r)

    index += 5
    pivot += 5
    return pivot, index

def add_walk_home(G, pivot, index):
    G.add_nodes_from(name_nodes[index:index+5])

    for i in range(1, 5):
        r = random.randint(-20, 20)
        G.add_edge(index, index + i, weight=200+r)
        G.add_edge(index + i, index, weight=200+r)
        houses.append(index + i)

    r = random.randint(-10, 10)
    G.add_edge(index + 1, index + 2, weight=300+r)
    G.add_edge(index + 2, index + 1, weight=300+r)

    G.add_edge(index + 3, index + 4, weight=300+r)
    G.add_edge(index + 4, index + 3, weight=300+r)

    index += 5
    pivot += 5
    return pivot, index

G, pivot, index = initialize_graph()

for i in range(39):
    r = random.randint(1, 2)
    if r == 1:
        pivot, index = add_hourglass(G, pivot, index)
    elif r == 2:
        pivot, index = add_walk_home(G, pivot, index)

G.add_edge(0, 1, weight=1)
G.add_edge(1, 0, weight=1)

f = 1
while f < index:
    r = random.randint(1, 2)
    if r == 1:
        G.add_edge(f, f+6, weight=1)
        G.add_edge(f+6, f, weight=1)
    elif r == 2:
        G.add_edge(f, f+5, weight=1)
        G.add_edge(f+5, f, weight=1)
    f += 5


# Leftover edges not in hourglass
G.add_nodes_from(list(range(197, 200)))
for i in range(197, 200):
    G.add_edge(i, i+1, weight=1)
    G.add_edge(i+1, i, weight=1)

G.add_edge(0, 199, weight=1)
G.add_edge(199, 0, weight=1)

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
print(len(matrix), len(matrix[0]))
print(houses)


houses = random.sample(houses, NUM_TAS)


name_nodes = [str(i) for i in name_nodes]
houses = [str(i) for i in houses]

create_dummy_output(N, houses)
save_input_to_file(N, N, len(houses), name_nodes, houses, '0', matrix)

# nx.draw(G, with_labels=True)
# plt.show()
