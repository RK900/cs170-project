"""
Calculate the ratio between walking home and the calculated optimal solution
"""

import os
import networkx as nx
from matplotlib import pyplot
from output_validator import validate_output, input_validator
import utils
from student_utils import *

def calc_output_file_ratio(output_file, input_folder="phase2_inputs/", outputs_folder="phase2_outputs"):
    input_file = output_file[:-len(".out")] + ".in"
    input_validator.VALID_FILENAMES.append(input_file)
    msg, calculated_score, err = validate_output(input_folder + input_file, outputs_folder + output_file)
    input_data = utils.read_file(input_folder + input_file)
    num_of_locations, num_houses, list_locations, list_houses, starting_car_location, adjacency_matrix = data_parser(
        input_data)
    G, message = adjacency_matrix_to_graph(adjacency_matrix)
    car_cycle = convert_locations_to_indices([starting_car_location], list_locations)
    dropoffs = {car_cycle[0]: convert_locations_to_indices(list_houses, list_locations)}
    soda_cost, solution_message = cost_of_solution(G, car_cycle, dropoffs)

    print(input_file, calculated_score, soda_cost)
    ratio = calculated_score/soda_cost
    return min(ratio, 1)
