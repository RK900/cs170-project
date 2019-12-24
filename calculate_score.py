"""
Calculate the sum of the ratio between walking home and the calculated solution
in a multithreaded fashion
"""
import os
import sys
from student_utils import *
import calc_output
import multiprocessing as mp
import itertools

def calculate_score(input_folder="phase2_inputs/", output_folder="phase2_outputs/"):
    pool = mp.Pool(mp.cpu_count())

    outputs = sorted(os.listdir(output_folder))
    estimated_score = 0
    num_inputs = len(outputs)
    results = pool.starmap(calc_output.calc_output_file_ratio, zip(outputs, itertools.repeat(input_folder), itertools.repeat(output_folder)))
    pool.close()
    return sum(results)/num_inputs * 100 

if __name__ == "__main__":
    print(calculate_score())