from mip.model import *

from student_utils import *
from utils import *


def build_nx_graph_given_file(input_file):
	# Used adjacency_matrix_to_graph instead of other version to provide names to locations and labels to them
	num_of_locations, num_houses, list_locations, list_houses, starting_car_location, adjacency_matrix = data_parser(
		input_file)
	return build_graph_given(num_of_locations, num_houses, list_locations,
							 list_houses, starting_car_location, adjacency_matrix)


# For optimization of skipping to write to file
def build_graph_given(num_of_locations, num_houses, list_locations, list_houses, starting_car_location,
					  adjacency_matrix):
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


def solve(graph, list_locations, list_houses, starting_car_location):
	shortest_path_all_pairs = nx.all_pairs_dijkstra_path_length(graph)  # Shortest path between all vertices
	TA = list_houses  # Vertex of the location of the TA at that spot

	m = Model(sense=MINIMIZE, solver_name=GUROBI)  # use GRB for Gurobi
	# variable that represents if the car takes the route
	x = [m.add_var(name='car_taken_{}'.format(u, v), var_type=BINARY) for (u, v) in graph.edges()]

	for loc in list_locations:
		incident_outgoing_edges = graph.in_edges(loc) + graph.out_edges(loc)
		m += xsum(x[u][v] for (u, v) in incident_outgoing_edges) % 2 == 0, 'verify_even_car_routes_{}'.format(loc)

	T = {}
	for house in list_houses:
		for loc in list_locations:
			T[house][loc] = m.add_var(
				name='ta_dropped_off_{}'.format(house), var_type=BINARY)

		m += xsum(T[house]) == 1  # Each ta must be dropped off

	w = [m.add_var(name='flow_in_{}'.format(house), var_type=BINARY) if house != starting_car_location else 1
		 for house in list_houses]

	for loc in list_locations:
		incoming_edges = graph.in_edges(loc)
		m += any(x[u][v] * w[v] for (u, v) in incoming_edges) - w_i[i] == 0, 'verify_connected_loc_{}'.format(loc)

	car_travel = 2 / 3 * xsum(x[u][v] * d['weight'] * w[v] for (u, v, d) in graph.edges(data=True))

	ta_travel = 1 * xsum(xsum(T[loc][ta] * shortest_path_all_pairs[loc][ta] * w[loc]
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
	return m.objective_value, m.objective_bound, x, T


def get_path_car_taken_from_vars(x, T, list_locations, list_houses, starting_location):
	stack = Stack()
	visited_edges = set()
	path_car_taken = [starting_location]
	for (u, v) in g.out_edges(starting_location):
		if x[u][v].x >= 0.99:
			stack.push((u, v))
	while not stack.isEmpty():
		(u, v) = stack.pop()
		if v not in path_car_taken:
			path_car_taken.append(v)
		visited_edges.add((u, v))
		for (u, v) in g.out_edges(v):
			if x[u][v].x >= 0.99:
				stack.push((u, v))
	student_drop_off_locations = []

	list_drop_of_locs = list_houses[:]
	for loc in list_locations:
		dropped_off = []
		for ta in list_drop_of_locs[:]:
			if T[ta][loc]:
				dropped_off.append(ta)
				list_drop_of_locs.remove(ta)
		student_drop_off_locations.append(dropped_off)
	for ta_left in list_drop_of_locs:
		student_drop_off_locations.append([ta_left, ta_left])
	return path_car_taken, list_drop_of_locs
