from mip.model import *

from student_utils import *
from utils import *


def solve(graph, list_locations, list_houses, starting_car_location):
	shortest_path_all_pairs = nx.all_pairs_dijkstra_path_length(graph)  # Shortest path between all vertices
	m = Model(sense=MINIMIZE, solver_name=CBC)  # use GRB for Gurobi
	# variable that represents if the car takes the route
	x = {(u, v): m.add_var(name='car_taken_{}'.format(u, v), var_type=BINARY) for (u, v) in graph.edges()}

	for loc in list_locations:
		incoming_edges = list(graph.in_edges(loc))
		outgoing_edges = list(graph.out_edges(loc))
		m += xsum(x[(u, v)] for (u, v) in incoming_edges) == xsum(
			x[(u, v)] for (u, v) in outgoing_edges), 'verify_even_car_routes_{}'.format(loc)

	T = {}
	for house in list_houses:
		for loc in list_locations:
			T[(house, loc)] = m.add_var(
				name='ta_dropped_off_{}_{}'.format(house, loc), var_type=BINARY)

		m += xsum(T[house, loc] for loc in list_locations) == 1  # Each ta must be dropped off

	# for (i, j) in set(product(set(V) - {0}, set(V) - {0})):
	# 	model += y[i] - (n + 1) * x[i][j] >= y[j] - n

	w = {house: m.add_var(name='flow_in_{}'.format(house), var_type=BINARY) if house != starting_car_location else 1
		 for house in list_locations}

	for loc in list_locations:
		incoming_edges = list(graph.in_edges(loc))
		m += xsum(w[v] for (u, v) in incoming_edges) - xsum(x[(u, v)] for (u, v) in incoming_edges) - w[
			loc] >= 1, 'verify_connected_loc_{}'.format(
			loc)

	car_travel = 2 / 3 * xsum(x[(u, v)] * d['weight'] * w[v] for (u, v, d) in graph.edges(data=True))

	ta_travel = 1 * xsum(xsum(T[(ta, loc)] * shortest_path_all_pairs[loc][ta] * w[loc]
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
