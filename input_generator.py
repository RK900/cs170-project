import datetime
import os
import random
import tempfile
from string import ascii_lowercase

import numpy as np

from branch_cut_lp_solver import build_graph_given, solve, get_path_car_taken_from_vars
from input_validator import quick_validate

dir_path = os.path.dirname(os.path.realpath(__file__))


def getUUIDLabel():
	return ''.join(random.choices(ascii_lowercase, k=20))


def save_test_to_file(N, num_of_locations=None, num_houses=None, list_locations=None, list_houses=None,
					  starting_car_location=None,
					  adjacency_matrix=None, provided_input=False):
	temp = create_temp_file(N)
	if not provided_input:
		num_of_locations, num_houses, list_locations, list_houses, starting_car_location, adjacency_matrix = create_valid_test_input(
			N)
	temp.writelines(str(num_of_locations) + "\n")
	temp.writelines(str(num_houses) + "\n")
	temp.writelines(" ".join(list_locations) + "\n")
	temp.writelines(" ".join(list_houses) + "\n")
	temp.writelines(starting_car_location + "\n")
	temp.writelines("\n".join([" ".join(map(str, row)) for row in adjacency_matrix]))


def save_output_file(N, path_car_taken, list_drop_of_locs, input_file_name=""):
	temp = create_temp_file(N, folder="outputs", prefix=input_file_name, file_extension=".out")
	temp.writelines(" ".join(path_car_taken) + "\n")
	temp.writelines(str(len(list_drop_of_locs)) + "\n")
	for drop_of_locs in list_drop_of_locs:
		temp.writelines(" ".join(drop_of_locs) + "\n")


def create_temp_file(N, folder="inputs", prefix="", file_extension=".in"):
	curr_time = datetime.datetime.now().strftime("%I:%M%p on %B %d, %Y")
	temp_dir = os.path.join(dir_path, folder, str(N))
	temp = tempfile.NamedTemporaryFile(
		delete=False, mode='w+t', prefix=prefix + "{}".format(curr_time), dir=temp_dir, suffix=file_extension)
	return temp


def create_valid_test_input(N):
	num_of_locations, num_houses, list_locations, list_houses, starting_car_location, adjacency_matrix = create_test_input(
		N)
	while not quick_validate(num_of_locations, num_houses, list_locations, list_houses, starting_car_location,
							 adjacency_matrix):
		num_of_locations, num_houses, list_locations, list_houses, starting_car_location, adjacency_matrix = create_test_input(
			N)
	return num_of_locations, num_houses, list_locations, list_houses, starting_car_location, adjacency_matrix


def create_test_input(N, uniform=True,
					  delete_edge_prob=0.05):  # TODO Possible mutate inputs so that good inputs are updated
	matrix = [[0.0] * N for i in range(N)]
	for i in range(N):
		for j in range(N):
			if i == j:
				matrix[i][j] = 'x'
				matrix[j][i] = 'x'
				continue

			if np.random.uniform(0, 1) < delete_edge_prob:
				matrix[i][j] = 'x'
				matrix[j][i] = 'x'
			elif uniform:
				x = np.random.uniform(50, 99)
				uniformRes = round(x, 5)
				matrix[i][j] = uniformRes
				matrix[j][i] = uniformRes
			else:
				expRes = np.random.exponential(1 / 12)
				matrix[i][j] = expRes
				matrix[j][i] = expRes

	list_of_locations = [str(i) for i in range(N)]
	numTA = round(N / 2)
	taLocIndex = np.random.choice(range(N), numTA, replace=False)
	list_of_homes = [list_of_locations[i] for i in taLocIndex]
	start_car_position = list_of_locations[0]
	return len(list_of_locations), len(list_of_homes), list_of_locations, list_of_homes, start_car_position, matrix


# Possible implement genetic algorthim for improvement
if __name__ == '__main__':
	num_of_locations, num_houses, list_locations, list_houses, starting_car_location, adjacency_matrix = create_valid_test_input(
		50)
	print("Completed input")
	print(len(list_houses))
	# input_data = utils.read_file('inputs/tests/multiple.in')

	# num_of_locations, num_houses, list_locations, list_houses, starting_car_location, adjacency_matrix = data_parser(
	# 	input_data)
	save_test_to_file(50, num_of_locations, num_houses, list_locations, list_houses, starting_car_location,
	                  adjacency_matrix, provided_input=True)
	G, list_locations, list_houses, starting_car_location = build_graph_given(num_of_locations, num_houses,
																			  list_locations, list_houses,
																			  starting_car_location, adjacency_matrix)
	objective_value, objective_bound, x, T = solve(G, list_locations, list_houses, starting_car_location)
	path_taken, dropped_off = get_path_car_taken_from_vars(G, x, T, list_locations, list_houses, starting_car_location)
	print(path_taken)
	print(dropped_off)
	save_output_file(num_of_locations, path_taken, dropped_off)
