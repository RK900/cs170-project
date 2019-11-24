from matplotlib import pyplot
from mip.model import *

from student_utils import *
from utils import *


def solve(graph, list_locations, list_houses, starting_car_location):
	shortest_path_all_pairs = nx.all_pairs_dijkstra_path_length(graph)  # Shortest path between all vertices
	shortest_path_all_pairs_dic = {}
	for item in shortest_path_all_pairs:
		shortest_path_all_pairs_dic[item[0]] = item[1]

	m = Model(sense=MINIMIZE, solver_name=CBC)  # use GRB for Gurobi
	# variable that represents if the car takes the route
	X = {}
	for (u, v) in graph.edges():
		X[(u, v)] = m.add_var(name='car_taken_{}_{}'.format(u, v),
							  var_type=BINARY)  # edges that are connected to source
	total_flow = len(list_houses)
	C = {}
	for (u, v) in graph.edges():
		C[(u, v)] = m.add_var(name='flow_on_edge_{}_{}'.format(u, v),
							  var_type=INTEGER)  # edges that are connected to source
		m += C[(u, v)] >= 0
		m += C[(u, v)] <= total_flow  # each edge cannot pass more than houses - 1
		m += C[(u,v)] <= (total_flow) * X[(u, v)]
	T = {}
	for ta in list_houses:
		for loc in list_locations:
			T[(ta, loc)] = m.add_var(
				name='ta_dropped_off_at_{}_walked_to_{}'.format(loc, ta), var_type=BINARY)
			incoming_edges = list(graph.in_edges(loc))
			m += xsum(X[(u, v)] for (u, v) in incoming_edges) >= T[(ta, loc)]  # if sum is 0 then T has to be 0
		m += xsum(T[(ta, loc)] for loc in list_locations) == 1  # Each ta must be dropped off


	for loc in list_locations:
		incoming_edges = list(graph.in_edges(loc))
		outgoing_edges = list(graph.out_edges(loc))
		m += xsum(X[(u, v)] for (u, v) in incoming_edges) == xsum(
			X[(u, v)] for (u, v) in outgoing_edges), 'verify_even_car_routes_{}'.format(loc)
		
		if loc == starting_car_location:
			m += xsum(X[(u, v)] for (u, v) in incoming_edges) >= 1
			m += xsum(X[(u, v)] for (u, v) in outgoing_edges) >= 1
			m += xsum(C[edge] for edge in outgoing_edges) == total_flow
			continue

		m += xsum(C[(u, v)] for (u, v) in incoming_edges) - xsum(C[(u, v)] for (u, v) in outgoing_edges) == xsum(T[(ta, loc)] for ta in list_houses) 		
		
	car_travel = 2 / 3 * xsum(X[(u, v)] * d['weight'] for (u, v, d) in graph.edges(data=True))

	ta_travel = 1 * xsum(
		xsum(T[(ta, loc)] * shortest_path_all_pairs_dic[loc][ta] for loc in list_locations) for ta in list_houses)

	m.objective = car_travel + ta_travel

	m.max_gap = 0.01
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
	return m.objective_value, m.objective_bound, X, T
