from matplotlib import pyplot
from mip.model import *

from student_utils import *
from utils import *


def solve(graph, list_locations, list_houses, starting_car_location):
	shortest_path_all_pairs = nx.all_pairs_dijkstra_path_length(graph)  # Shortest path between all vertices
	shortest_path_all_pairs_dic = {}
	for item in shortest_path_all_pairs:
		shortest_path_all_pairs_dic[item[0]] = item[1]
	m = Model(sense=MINIMIZE, solver_name=GUROBI)  # use GUROBI, use CBC for other
	# variable that represents if the car takes the route
	x = {(u, v): m.add_var(name='car_taken_{}_{}'.format(u, v), var_type=BINARY) for (u, v) in graph.edges()}

	for loc in list_locations:
		incoming_edges = list(graph.in_edges(loc))
		outgoing_edges = list(graph.out_edges(loc))
		m += xsum(x[(u, v)] for (u, v) in incoming_edges) == xsum(
			x[(u, v)] for (u, v) in outgoing_edges), 'verify_even_car_routes_{}'.format(loc)

	# edges = graph.edges()
	# E = len(edges)
	# U = {(u, v): m.add_var(name='edge_ordering_{}_{}'.format(u, v), var_type=INTEGER) for (u, v) in graph.edges()}
	# # print(U)
	# for (u, v) in edges:
	# 	m += U[(u, v)] >= 0
	# 	m += U[(u, v)] <= E - 1
	# 	for (i, j) in edges:
	# 		if i != u and i != starting_car_location and u != starting_car_location:
	# 			m += U[(u, v)] - U[(i, j)] + E * (x[(i, j)]) <= E - 1

	u = {location: m.add_var(name='dummy_{}'.format(location), var_type=INTEGER) for location in list_locations}
	m += u[starting_car_location] == 1
	n = len(list_locations)
	for i in list_locations:
		if i != starting_car_location:
			m += u[i] >= 2
			m += u[i] <= n
		for j in list_locations:
			if i != j and i != starting_car_location and j != starting_car_location and (i, j) in x:
				m += u[i] - u[j] + 1 <= (n - 1) * (1 - x[(i, j)])

	T = {}
	for house in list_houses:
		for loc in list_locations:
			T[(house, loc)] = m.add_var(
				name='ta_dropped_off_at_{}_walked_to_{}'.format(loc, house), var_type=BINARY)
			incoming_edges = list(graph.in_edges(loc))
			# incoming_edges_house = list(graph.in_edges(house))
			m += xsum(x[(u, v)] for (u, v) in incoming_edges) - T[(house, loc)] >= 0  # if sum is 0 then T has to be 0
			if house == loc:
				m += xsum(x[(u, v)] for (u, v) in incoming_edges) <= T[
					(house, loc)]  # if at house then it's 1 if bounded

		# if loc == house:
		# 	m +=
		# m += xsum(x[(u, v)] for (u, v) in incoming_edges) - T[(house, loc)] >= 0

		m += xsum(T[(house, loc)] for loc in list_locations) == 1  # Each ta must be dropped off

	car_travel = 2 / 3 * xsum(x[(u, v)] * d['weight'] for (u, v, d) in graph.edges(data=True))

	ta_travel = 1 * xsum(xsum(T[(house, loc)] * shortest_path_all_pairs_dic[loc][house]
							  for loc in list_locations) for house in list_houses)

	m.objective = car_travel + ta_travel

	m.max_gap = 0.02
	status = m.optimize()
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

