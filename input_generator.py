import numpy as np
import random
import string
import tempfile
import os
import uuid
import datetime
from input_validator import validate_input, quick_validate

dir_path = os.path.dirname(os.path.realpath(__file__))

def getUUIDLabel():
   return str(uuid.uuid4())


def save_test_to_file(N, num_of_locations, num_houses, list_locations, list_houses, starting_car_location, adjacency_matrix):
    temp = create_temp_file(N)
    num_of_locations, num_houses, list_locations, list_houses, starting_car_location, adjacency_matrix = create_valid_test_input(
        N)
    temp.writelines(num_of_locations)
    temp.writelines(len(num_houses))
    temp.writelines("".join(list_locations))
    temp.writelines("".join(list_houses))
    temp.writelines(starting_car_location)
    temp.writelines(" ".join([" ".join(row) for row in adjacency_matrix]))


def save_output_file(N, path_car_taken, list_drop_of_locs, input_file_name=""):
    temp = create_temp_file(N, folder="outputs", prefix=input_file_name, file_extension=".out")
    temp.writelines(" ".join(path_car_taken))
    temp.writelines(len(list_drop_of_locs))
    for drop_of_locs in list_drop_of_locs:
        temp.writelines(" ".join(drop_of_locs))

def create_temp_file(N, folder="inputs", prefix="", file_extension=".in"):
    curr_time = datetime.datetime.now().strftime("%I:%M%p on %B %d, %Y")
    temp_dir = os.path.join(dir_path, folder, str(N))
    temp = tempfile.NamedTemporaryFile(
        delete=False, mode='w+t', prefix=prefix + "-{}".format(curr_time), dir=temp_dir, suffix=file_extension)
    return temp

def create_valid_test_input(N):
    num_of_locations, num_houses, list_locations, list_houses, starting_car_location, adjacency_matrix = create_test_input(
        N)
    while not quick_validate(num_of_locations, num_houses, list_locations, list_houses, starting_car_location, adjacency_matrix):
           num_of_locations, num_houses, list_locations, list_houses, starting_car_location, adjacency_matrix = create_test_input(
               N)
    return num_of_locations, num_houses, list_locations, list_houses, starting_car_location, adjacency_matrix


def create_test_input(N, uniform=True, delete_edge_prob=0): # TODO Possible mutate inputs so that good inputs are updated
    matrix = [[0] * N] * N
    for i in range(int(N/2)):
        for j in range(int(N/2)):
            print(i, j)
            if i == j:
                continue
            if np.random.uniform(0, 1) < delete_edge_prob:
                matrix[i][j] = 'x'
                matrix[j][i] = 'x'

            if uniform:
                uniformRes = np.random.uniform(0, 1)
                matrix[i][j] = uniformRes
                matrix[j][i] = uniformRes
            else:
                expRes = numpy.random.exponential(1/12)
                matrix[i][j] = expRes
                matrix[j][i] = expRes
            
    list_of_locations = [getUUIDLabel() for i in range(N)]
    numTA = round(np.random.uniform(0, N/2))
    taLocIndex = np.random.choice(range(N), numTA)
    list_of_homes = [list_of_locations[i] for i in taLocIndex]
    start_car_position = list_of_locations[0]
    return len(list_of_locations), len(list_of_homes), list_of_locations, list_of_homes, start_car_position, matrix

# Possible implement genetic algorthim for improvement
if __name__ == '__main__':
    save_test_to_file(5, 5, 5, 5, 5, 5, 5)
