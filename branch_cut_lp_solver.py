import networkx
from matplotlib import pyplot
from mip.callbacks import ConstrsGenerator, CutPool
from mip.model import *
from mip.model import Model, xsum, BINARY

from student_utils import *
from utils import *


class SubTourCutGenerator(ConstrsGenerator):
	def __init__(self, graph, list_locations, starting_loc):
		self.graph = graph
		self.list_locations = list_locations
		self.starting_loc = starting_loc

	def generate_constrs(self, model: Model):
		G = nx.DiGraph()
		# G.add_nodes_from(self.list_locations)
		r = [(v, v.x) for v in model.vars if v.name.startswith('car_taken')]
		U = [v.name.split('(')[1].split(',')[0] for v, f in r]
		V = [v.name.split(')')[0].split(',')[1] for v, f in r]

		cp = CutPool()
		for i in range(len(U)):
			if r[i][1] >= 1:
				G.add_edge(U[i], V[i], capacity=r[i][1])
		Components = list(networkx.strongly_connected_components(G))
		if len(Components) == 1:
			return
		for S in Components:
			if self.starting_loc in S:
				continue
			arcsInS = [(v, f) for i, (v, f) in enumerate(r) if U[i] in S and V[i] in S]
			if sum(f for v, f in arcsInS) > (len(S) - 1):
				cut = xsum(1.0 * v for v, fm in arcsInS) <= len(S) - 1
				cp.add(cut)

			# arcsInS = [(v, f) for i, (v, f) in enumerate(r) if U[i] in S and V[i] in S]
			# print(arcsInS)
			# cp.add(xsum(x[
		# i, j] for i in S for j in S if j > i) <= len(S) - 1)
		# for S in Components:
		# 	# model.addCons(quicksum(x[i, j] for i in S for j in S if j > i) <= len(S) - 1)
		# 	m +=
		# for loc in self.list_locations:
		# 	if loc == self.starting_loc:
		# 		continue
		# 	for other_loc in self.list_locations:
		# 		if other_loc != loc:
		# 			continue
		# 		# cut_value, (S, NS) = nx.minimum_cut(G, loc, other_loc)
		# 		# if (cut_value <= 0.99):
		# 		# 	arcsInS = [(v, f) for i, (v, f) in enumerate(r) if U[i] in S and V[i] in S]
		# 		# 	cut = xsum(x[a] for a in A if (a[0] in S and a[1] in S)) <= len(S) - 1
		# 		# 	cp.add(cut)
		# 		val, (S, NS) = nx.minimum_cut(G, loc, other_loc)
		#
		# 		if val <= 0.99:
		# 			arcsInS = [(v, f) for i, (v, f) in enumerate(r) if U[i] in S and V[i] in S]
		# 			# if sum(f for v, f in arcsInS) > (len(S) - 1):
		# 			cut = xsum(1.0 * v for v, fm in arcsInS) <= len(S) - 1
		#
		# 			cp.add(cut)
		# 				# if len(cp.cuts) > 256:
		# 				# 	for cut in cp.cuts:
		# 				# 		model += cut
		# 				# 	return

		for cut in cp.cuts:
			model += cut
		return


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
	for i, loc in enumerate(list_locations):
		for j, other_loc in enumerate(list_locations):
			if loc == other_loc:
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
	m = Model(sense=MINIMIZE, solver_name=GUROBI)  # use GUROBI, use CBC for other
	# variable that represents if the car takes the route
	x = {(u, v): m.add_var(name='car_taken({},{})'.format(u, v), var_type=BINARY) for (u, v) in graph.edges()}

	for loc in list_locations:
		incoming_edges = list(graph.in_edges(loc))
		outgoing_edges = list(graph.out_edges(loc))
		m += xsum(x[(u, v)] for (u, v) in incoming_edges) == xsum(
			x[(u, v)] for (u, v) in outgoing_edges), 'verify_even_car_routes_{}'.format(loc)

		if loc == starting_car_location:
			m += xsum(x[(u, v)] for (u, v) in incoming_edges) >= 1

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
		m += xsum(T[(house, loc)] for loc in list_locations) == 1  # Each ta must be dropped off

	car_travel = 2 / 3 * xsum(x[(u, v)] * d['weight'] for (u, v, d) in graph.edges(data=True))

	ta_travel = 1 * xsum(xsum(T[(house, loc)] * shortest_path_all_pairs_dic[loc][house]
							  for loc in list_locations) for house in list_houses)
	m.constrs_generator = SubTourCutGenerator(graph, list_locations, starting_car_location)
	m.constrs_generator.lazy_constraints = True
	m.lazy_constrs_generator = SubTourCutGenerator(graph, list_locations, starting_car_location)

	m.objective = car_travel + ta_travel

	# from random import shuffle
	# S = [i for i in range(n)]
	# shuffle(S)
	# model.start = [(x[S[k - 1]][S[k]], 1.0) for k in range(n)]
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
	return m.objective_value, m.objective_bound, x, T


def get_path_car_taken_from_vars(g, x, T, list_locations, list_houses, starting_location):
	stk = Stack()
	stk.lst = []
	visited_edges = set()
	path_car_taken = [starting_location]
	for (u, v) in g.out_edges(starting_location):
		if x[(u, v)].x >= 0.99:
			stk.push((u, v))
	G = nx.DiGraph()
	# G.add_nodes_from(list_locations)
	for (u, v) in g.out_edges(starting_location):
		if x[(u, v)].x >= 0.99:
			stk.push((u, v))

	for (u, v) in g.edges():
		if x[(u,v)].x >= 0.99:
			G.add_edge(u, v)

	nx.draw_networkx(G)
	pyplot.show()
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
