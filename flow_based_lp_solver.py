from mip.model import *

from student_utils import *
from utils import *


def build_nx_graph_given_file(input_file):
	# Used adjacency_matrix_to_graph instead of other version to provide names to locations and labels to them
	num_of_locations, num_houses, list_locations, list_houses, starting_car_location, adjacency_matrix = data_parser(
		input_file)
	return build_graph_given(num_of_locations, num_houses, list_locations, list_houses, starting_car_location,
							 adjacency_matrix)


# For optimization of skipping to write to file
def build_graph_given(num_of_locations, num_houses, list_locations, list_houses, starting_car_location,
					  adjacency_matrix):
	G = nx.DiGraph()
	G.add_nodes_from(list_locations)
	for i, loc in enumerate(list_locations):
		for j, other_loc in enumerate(list_locations):
			if i == j:
				continue
			if adjacency_matrix[i][j] == 'x':
				continue
			G.add_edge(loc, other_loc, weight=adjacency_matrix[i][j])
			G.add_edge(other_loc, loc, weight=adjacency_matrix[i][j])
	return G, list_locations, list_houses, starting_car_location


def solve(graph, list_locations, list_houses, starting_car_location):
	shortest_path_all_pairs = nx.all_pairs_dijkstra_path_length(graph)  # Shortest path between all vertices
	shortest_path_all_pairs_dic = {}
	for item in shortest_path_all_pairs:
		shortest_path_all_pairs_dic[item[0]] = item[1]

	m = Model(sense=MINIMIZE, solver_name=GUROBI)  # use GRB for Gurobi
	# variable that represents if the car takes the route
	C = {}
	for (u, v) in graph.edges():
		C[(u, v)] = m.add_var(name='car_taken_{}_{}'.format(u, v),
							  var_type=BINARY)  # edges that are connected to source
	F = {}
	for loc in list_locations:
		if loc == starting_car_location:
			F[starting_car_location] = 1
		else:
			F[loc] = m.add_var(name='flow_on_vertex_{}'.format(loc))

	for loc in list_locations:
		incoming_edges = list(graph.in_edges(loc))
		outgoing_edges = list(graph.out_edges(loc))

		m += xsum(C[(u, v)] for (u, v) in incoming_edges) == xsum(
			C[(u, v)] for (u, v) in outgoing_edges), 'verify_even_car_routes_{}'.format(loc)

		for (u, v) in incoming_edges:
			m += F[v] >= F[u] + C[(u, v)] - 1
			# Flow at each vertex is at least flow to previous vertex + edge capacity - 1. Checks if fi=1,Cij=1
			m += C[(u, v)] <= F[u]  # if there is no flow on pred edge then car cannot visit

		m += F[loc] <= xsum(C[(u, v)] for (u, v) in incoming_edges)

	T = {}
	for house in list_houses:
		for loc in list_locations:
			T[(house, loc)] = m.add_var(
				name='ta_dropped_off_at_{}_walked_to_{}'.format(loc, house), var_type=BINARY)
			incoming_edges = list(graph.in_edges(loc))
			# incoming_edges_house = list(graph.in_edges(house))
			m += xsum(C[(u, v)] for (u, v) in incoming_edges) - T[(house, loc)] >= 0  # if sum is 0 then T has to be 0
			if house == loc:
				m += xsum(C[(u, v)] for (u, v) in incoming_edges) <= T[
					(house, loc)]  # if at house then it's 1 if bounded

		m += xsum(T[(house, loc)] for loc in list_locations) == 1  # Each ta must be dropped off

	car_travel = 2 / 3 * xsum(C[(u, v)] * d['weight'] for (u, v, d) in graph.edges(data=True))

	ta_travel = 1 * xsum(xsum(T[(ta, loc)] * shortest_path_all_pairs_dic[loc][ta]
							  for loc in list_locations) for ta in list_houses)

	m.objective = car_travel + ta_travel

	m.max_gap = 0.02
	status = m.optimize(max_seconds=300)
	if status == OptimizationStatus.OPTIMAL:
		print('optimal solution cost {} found'.format(m.objective_value))
	elif status == OptimizationStatus.FEASIBLE:
		print('sol.cost {} found, best possible: {}'.format(
			m.objective_value, m.objective_bound))
	elif status == OptimizationStatus.NO_SOLUTION_FOUND:
		print('no feasible solution found, lower bound is: {}'.format(
			m.objective_bound))
	if status == OptimizationStatus.OPTIMAL or status == OptimizationStatus.FEASIBLE:
		print('solution:')
		for v in m.vars:
			if abs(v.x) > 1e-6:  # only printing non-zeros
				print('{} : {}'.format(v.name, v.x))
	return m.objective_value, m.objective_bound, C, T


def get_path_car_taken_from_vars(g, x, T, list_locations, list_houses, starting_location):
	stk = Stack()
	stk.lst = []
	visited_edges = set()
	path_car_taken = [starting_location]
	for (u, v) in g.out_edges(starting_location):
		if x[(u, v)].x >= 0.99:
			stk.push((u, v))
	while not stk.isEmpty():
		(u, v) = stk.pop()
		if (u, v) in visited_edges:
			continue
		path_car_taken.append(v)
		visited_edges.add((u, v))
		for (u, v) in g.out_edges(v):
			if x[(u, v)].x >= 0.99 and (u, v) not in visited_edges:
				stk.push((u, v))

	student_drop_off_locations = []
	list_drop_of_locs = list_houses[:]
	for loc in list_locations:
		dropped_off = []
		for ta in list_drop_of_locs[:]:
			if T[(ta, loc)].x >= 0.99:
				dropped_off.append(ta)
				list_drop_of_locs.remove(ta)
		if dropped_off:
			dropped_off = [loc] + dropped_off
			student_drop_off_locations.append(dropped_off)
	for ta_left in list_drop_of_locs:
		student_drop_off_locations.append([ta_left, ta_left])
	return path_car_taken, student_drop_off_locations