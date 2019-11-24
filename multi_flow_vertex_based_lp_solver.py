from matplotlib import pyplot
from mip.model import *

from student_utils import *
from utils import *


def solve(graph, list_locations, list_houses, starting_car_location, solver=CBC):
	shortest_path_all_pairs = nx.all_pairs_dijkstra_path_length(graph)  # Shortest path between all vertices
	shortest_path_all_pairs_dic = {}
	for item in shortest_path_all_pairs:
		shortest_path_all_pairs_dic[item[0]] = item[1]

	m = Model(sense=MINIMIZE, solver_name=solver)  # use GRB for Gurobi
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
		m += C[(u, v)] >= X[(u, v)]  # the existance of an edge is upper bounded by the flow at an edge

	F = {}
	for loc in list_locations:
		F[loc] = m.add_var(name='flow_on_vertex_{}'.format(loc), var_type=INTEGER)
		# at each vertex flow can be atleast 0 or 1
		m += F[loc] >= 0
		m += F[loc] <= total_flow

		if loc == starting_car_location:  # starting node has total flow
			m += F[starting_car_location] == total_flow

	# sum of flow on edges is at most 1
	m += xsum(C[edge] for edge in graph.in_edges(starting_car_location)) <= total_flow
	for loc in list_locations:
		incoming_edges = list(graph.in_edges(loc))
		outgoing_edges = list(graph.out_edges(loc))
		# Incoming edges = outgoing edges
		m += xsum(X[(u, v)] for (u, v) in incoming_edges) == xsum(
			X[(u, v)] for (u, v) in outgoing_edges), 'verify_even_car_routes_{}'.format(loc)

		for (u, v) in incoming_edges:
			# Flow at any destination is at least the ce edge to it
			m += F[v] >= C[(u, v)]
			m += C[(u, v)] <= F[u]  # The capacity edge has is upper bound by the flow from that vertex

		# flow to any vertex is upper bounded by sum of flow to that vertex
		m += F[loc] <= xsum(
			C[(u, v)] for (u, v) in incoming_edges)  # The flow at a location is at most sum of the capacities to it
		m += F[loc] <= total_flow * xsum(
			X[(u, v)] for (u, v) in incoming_edges)  # flow at edge is 0 if now edges go there

		if loc in list_houses:
			m += xsum(C[(u, v)] for (u, v) in incoming_edges) - 1 == xsum(C[(u, v)] for (u, v) in outgoing_edges)
		else:
			# If not a house flow is conserved or a starting location
			m += xsum(C[(u, v)] for (u, v) in incoming_edges) - xsum(C[(u, v)] for (u, v) in outgoing_edges) == 0

	T = {}
	for house in list_houses:
		for loc in list_locations:
			T[(house, loc)] = m.add_var(
				name='ta_dropped_off_at_{}_walked_to_{}'.format(loc, house), var_type=BINARY)
			incoming_edges = list(graph.in_edges(loc))
			# incoming_edges_house = list(graph.in_edges(house))
			m += xsum(X[(u, v)] for (u, v) in incoming_edges) - T[(house, loc)] >= 0  # if sum is 0 then T has to be 0
			if house == loc:
				m += xsum(X[(u, v)] for (u, v) in incoming_edges) <= T[(house, loc)]  # if at house then it's 1 if bounded

		m += xsum(T[(house, loc)] for loc in list_locations) == 1  # Each ta must be dropped off

	car_travel = 2 / 3 * xsum(X[(u, v)] * d['weight'] for (u, v, d) in graph.edges(data=True))

	ta_travel = 1 * xsum(
		xsum(T[(ta, loc)] * shortest_path_all_pairs_dic[loc][ta] for loc in list_locations) for ta in list_houses)

	m.objective = car_travel + ta_travel

	m.max_gap = 0.01
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