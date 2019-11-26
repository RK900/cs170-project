# coding=utf-8
import datetime
import os
import random
import tempfile
from string import ascii_lowercase

import numpy as np
import glob
import utils
from input_validator import quick_validate
from multi_flow_based_lp_solver import solve
# from multi_flow_based_lp_solver import build_graph_given, solve, get_path_car_taken_from_vars
from student_utils import data_parser
from utils import build_graph_given, get_path_car_taken_from_vars
from fix_output import fix_output

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


def save_input_to_file(N, num_of_locations=None, num_houses=None, list_locations=None, list_houses=None,
					   starting_car_location=None,
					   adjacency_matrix=None, provided_input=False):
	now = datetime.datetime.now()
	filename = str(N) + now.strftime('_%B%d_%H%M')
	path = 'inputs/%s/' % str(N) + filename
	with open(path + '.in', 'w') as temp:
		temp.writelines(str(num_of_locations) + "\n")
		temp.writelines(str(num_houses) + "\n")
		temp.writelines(" ".join(list_locations) + "\n")
		temp.writelines(" ".join(list_houses) + "\n")
		temp.writelines(starting_car_location + "\n")
		temp.writelines("\n".join([" ".join(map(str, row)) for row in adjacency_matrix]))
	
	return path + '.in'


def save_temp_output_file(N, path_car_taken, list_drop_of_locs, input_file_name=""):
	temp = create_temp_file(N, folder="outputs", prefix=input_file_name, file_extension=".out")
	temp.writelines(" ".join(path_car_taken) + "\n")
	temp.writelines(str(len(list_drop_of_locs)) + "\n")
	for drop_of_locs in list_drop_of_locs:
		temp.writelines(" ".join(drop_of_locs) + "\n")


def save_output_file(N, path_car_taken, list_drop_of_locs, input_file_name="",output_path=""):
	now = datetime.datetime.now()
	filename = str(N) + now.strftime('_%B%d_%H%M')
	path = 'outputs/%s/' % str(N) + filename + '.out'
	if output_path:
		path = output_path
	with open(path, 'w') as temp:
		temp.writelines((" ".join(path_car_taken) + "\n").encode('ascii', 'ignore').decode('ascii'))
		temp.writelines(str(len(list_drop_of_locs)) + "\n")
		for drop_of_locs in list_drop_of_locs:
			temp.writelines((" ".join(drop_of_locs) + "\n").encode('ascii', 'ignore').decode('ascii'))
	
	return path

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
					  delete_edge_prob=0.2):  # TODO Possible mutate inputs so that good inputs are updated
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
				x = np.random.uniform(0.5, 1)
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


def run(input_file="", random=False, size=50, draw=False, output_path="", output_log_path="", solver_mode="GRB",time_limit=None):
	"""
	Runs the solver using eithe random input or given the input file.

	Parameters
	----------
	input_file: str
		An optional input file to run the program with
	random: bool
		Uses a random input to generate the file
	size: int
		The size of the random input to use
	draw: bool
		A boolean to decide whether to draw the file
	output_path: str
		The output path to write the input to. If None, ignores it
	output_log_path: str
		Logges the optimal value and the bound. This is to see if time limit was hit and un optimal bound was found.
		If None, doesn't write a file
	solver_mode: str
		"GRB" for gurobi if the license exists and "CBC" for open source CBC
	time_limit: int
		The number of seconds to timeout the optimzer. If none is passed, no timelimit.
	"""
	if random:
		num_of_locations, num_houses, list_locations, list_houses, starting_car_location, adjacency_matrix = create_valid_test_input(
			size)
	else:
		print(input_file)
		input_data = utils.read_file(input_file)

		num_of_locations, num_houses, list_locations, list_houses, starting_car_location, adjacency_matrix = data_parser(
			input_data)
	# print("completed input")
	G, list_locations, list_houses, starting_car_location = build_graph_given(num_of_locations, num_houses,
																			  list_locations, list_houses,
																			  starting_car_location, adjacency_matrix)
	objective_value, objective_bound, x, T = solve(G, list_locations, list_houses, starting_car_location, solver_mode=solver_mode,time_limit=time_limit)
	path_taken, dropped_off = get_path_car_taken_from_vars(G, x, T, list_locations, list_houses, starting_car_location,
														   draw=draw)
	# print(path_taken)
	# print(dropped_off)

	if random:
		print('Input file written to: ' + save_input_to_file(size, num_of_locations, num_houses, list_locations, list_houses, starting_car_location,
						  adjacency_matrix, provided_input=True))
	write_path = save_output_file(num_of_locations, path_taken, dropped_off, output_path=output_path)
	fix_output(write_path, full_path=True)
	# print('Output file written to: ' + write_path)
	if output_log_path:
		with open(output_log_path, 'w') as f:
			f.write('objective value: ' + str(objective_value) + '\n')
			f.write('objective bound: ' + str(objective_bound) + '\n')



		# save_log_path(objective_value, output_path=output_log_path)


def run_batch_inputs(input_folder, file_range=[1, 5], extensions=['50','100','200'], solver_mode='GRB', time_limit=10000):
	files = []
	for i in range(file_range[0], file_range[1] + 1):
		for extension in extensions:
			files.append("{}_{}".format(i, extension))
	for input_file in files:
		print(input_file)
		if os.path.isfile('phase2_inputs/{}.in'.format(input_file)):
			run(input_file='phase2_inputs/{}.in'.format(input_file),draw=False,output_path='phase2_outputs/{}.out'.format(input_file), 
			output_log_path='phase2_log/{}-log.out'.format(input_file), solver_mode=solver_mode,time_limit=time_limit)
	# for file in glob.glob(os.path.join(dir_path, input_folder) + '/[{}-{}].*'.format(range[0],range[1])):
		# print(file)



# Possible implement genetic algorthim for improvement
if __name__ == '__main__':
	run_batch_inputs('phase2_inputs', file_range=[281, 300], extensions=['100'])
	# print("Completed input")
	# run(random=True, size=50, draw=False)
	# run('inputs/200.in')
	# print("Completed input")
	# run('inputs/tests/9_50.in', draw=False)
	# run('inputs/tests/multiple.in', draw=False)
	# run('inputs/tests/modified_hourglass.in', draw=True)
	# run('final_inputs/inputs/200.in')
	# run(random=True)
	# run('final_inputs/inputs/200.in')
	# print(len(list_houses))
	# run('inputs/tests/test.in', draw=False)
