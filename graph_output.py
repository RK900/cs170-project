from matplotlib import pyplot
import networkx as nx

def graph_output(input_file_name):
    path = "phase2_outputs/{}.out".format(input_file_name)
    with open(path, 'r') as f:
        content = f.readlines()
    
    old_route = content[0][:]
    old_route = old_route.split()
    edges = []
    G = nx.DiGraph()
    for i in range(1, len(old_route)):
        if old_route[i] == '\n':
            continue
        G.add_edge(old_route[i - 1], old_route[i])
        edges.append((old_route[i - 1], old_route[i]))
    # print(edges)
    # for (u, v) in G.edges():
    #     if (u,v) in edges:
            

    nx.draw_networkx(G)
    pyplot.show()

if __name__ == "__main__":
    graph_output('71_200')
