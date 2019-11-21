# project-fa19
CS 170 Fall 2019 Project
## Proposal
### Inputs/Outputs 
We generate inputs and outputs randomly. Then, we place the TA locations randomly through the graph.
We run a solver through the nodes and time it. The graphs that take the longest to solve are the ones provided as input.
### LP
We aim to solve the problem mainly through integer linear programming. We use the following given components of our lp: shortest path between all nodes and the distance between vertex i and j.

We define the variable x[i][j] as an indicator variable to be 1 if the car takes the route and 0 if the car doesn't take the route. Since we want to make sure that the source vertex makes a round trip we ensure that for each vertex the sum of x_ij of incoming + outgoing is an even number

To handle Ta walking home we define Ta[i][b] as an indicator variable  to be if the ta was dropped off at that vertex with 1 = dropped of at vertex 0 if not. To verify that each Ta goes home we constraint the sum of each Ta[i] == 1.

As we were building our lp, we realized that we could be creating invalid subtours. Then, we got inspired by the idea of flow to verify that each tour is connected to source. We define w as an indicator variable where 1 if flow on that vertex and 0 if no flow. We define the flow of the source vertex to be 1. Then, for all vertices if it has a edge where the vertex of the incoming edge has flow 1 set the current flow to be 1. This ensures that subtours are connected.

Our objective function is then: min 2/3 \sum_{(u,v) for all edges} x_ij * w_j * d_ij + 1 * \sum_{i in TA} \sum{v in V} T[i][v] * ShortestPath(v, i) * w[v]
