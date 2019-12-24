import os
import networkx as nx
from matplotlib import pyplot
import utils
from student_utils import *

def get_files_with_extension(directory, extension):
	files = []
	for name in os.listdir(directory):
		if name.endswith(extension):
			files.append(f'{directory}/{name}')
	return files


def read_file(file):
	# print("reading_file", file)
	with open(file, 'r', encoding="utf-8") as f:
		data = f.readlines()
	data = [line.replace("Â", " ").strip().split() for line in data]
	return data


def write_to_file(file, string, append=False):
	if append:
		mode = 'a'
	else:
		mode = 'w'
	with open(file, mode) as f:
		f.write(string)


def write_data_to_file(file, data, separator, append=False):
	if append:
		mode = 'a'
	else:
		mode = 'w'
	with open(file, mode) as f:
		for item in data:
			f.write(f'{item}{separator}')


def input_to_output(input_file):
	return input_file.replace('input', 'output').replace('.in', '.out')


class Stack:
	"A container with a last-in-first-out (LIFO) queuing policy."

	def _init_(self):
		self.lst = []

	def push(self, item):
		"Push 'item' onto the stack"
		self.lst.append(item)

	def pop(self):
		"Pop the most recently pushed item from the stack"
		return self.lst.pop()

	def isEmpty(self):
		"Returns true if the stack is empty"
		return len(self.lst) == 0

	def __repr__(self):
		return " ".join(self.lst)

def build_nx_graph_given_file(input_file):
	# Used adjacency_matrix_to_graph instead of other version to provide names to locations and labels to them
	num_of_locations, num_houses, list_locations, list_houses, starting_car_location, adjacency_matrix = data_parser(
		input_file)
	return build_graph_given(num_of_locations, num_houses, list_locations, list_houses, starting_car_location,
							 adjacency_matrix)

# For optimization of skipping to write to file
def build_graph_given(num_of_locations, num_houses, list_locations, list_houses, starting_car_location,
					  adjacency_matrix, draw=False):
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
	if draw:
		pos = nx.spring_layout(G)
		labels = nx.get_edge_attributes(G, 'weight')
		nx.draw(G, pos)
		nx.draw_networkx_edge_labels(G, pos, edge_labels=labels)
		plt.show() 
	return G, list_locations, list_houses, starting_car_location


def get_path_car_taken_from_vars(g, x, T, list_locations, list_houses, starting_location, draw=False):
	stk = Stack()
	stk.lst = []
	visited_edges = set()
	path_car_taken = [starting_location]
	for (u, v) in g.out_edges(starting_location):
		if x[(u, v)].x >= 0.99:
			stk.push((u, v))
	if draw:
		G = nx.DiGraph()
		for (u, v) in g.edges():
			if x[(u, v)].x >= 0.99:
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

