import os
import sys
from student_utils import *
import utils
from output_validator import validate_output, input_validator

outputs = os.listdir('phase2_outputs/')
estimated_score = 0
num_inputs = len(outputs)
for output_file in outputs:
    input_file = output_file[:-len(".out")] + ".in"
    input_validator.VALID_FILENAMES.append(input_file)
    msg, calculated_score, err = validate_output("phase2_inputs/" + input_file, "phase2_outputs/" + output_file)
    # print(msg, calculated_score, err)
    input_data = utils.read_file("phase2_inputs/" + input_file)
    num_of_locations, num_houses, list_locations, list_houses, starting_car_location, adjacency_matrix = data_parser(
        input_data)
    G, message = adjacency_matrix_to_graph(adjacency_matrix)
    car_cycle = convert_locations_to_indices([starting_car_location], list_locations)
    dropoffs = {car_cycle[0]: convert_locations_to_indices(list_houses, list_locations)}
    soda_cost, solution_message = cost_of_solution(G, car_cycle, dropoffs)

    # print(input_file, calculated_score, soda_cost)
    ratio = calculated_score/soda_cost
    if ratio > 1:
        print("FAILURE")
        print(input_file + " " + str(calculated_score) + " " + str(soda_cost))
        # raise Exception(input_file + " " + str(calculated_score) + " " + str(soda_cost))
    estimated_score += ratio
print(estimated_score/num_inputs*100)
    # diff = abs((item[1] - item[0])/item[1])
    # if diff > err:
    #     i += 1
    #     print(item[2], item[1], item[0], diff)
# print("{} items with error greater than {}".format(i, err))
