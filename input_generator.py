import numpy
import random
import string
import tempfile
import os
import uuid

dir_path = os.path.dirname(os.path.realpath(__file__))

def getUUIDLabel():
   return str(uuid.uuid4())



def create_test_input(N, uniform=True, delete_edge_prob=0): # TODO Possible mutate inputs so that good inputs are updated
    matrix = [[0] * N] * N
    for i in range(N/2):
        for j in range(N/2):
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
    taLocIndex = np.random.choice(range(N), numTa)
    list_of_homes = [randomNames[i] for i in taLocIndex]
    start_car_position = list_of_locations[0]
    return len(list_of_locations), len(list_of_homes), list_of_locations, list_of_homes, start_car_position, matrix

# Possible implement genetic algorthim for improvement
