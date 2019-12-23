"""
Calculate the sum of the ratio between walking home and the calculated solution
in a multithreaded fashion
"""
import os
import sys
from student_utils import *
import calc_output
import multiprocessing as mp

def calculate_score(output_folder):
    pool = mp.Pool(mp.cpu_count())

    outputs = sorted(os.listdir(output_folder))
    estimated_score = 0
    num_inputs = len(outputs)
    results = pool.map(calc_output.calc_output_file_ratio, outputs)
    pool.close()
    return sum(results)/num_inputs * 100 

if __name__ == "__main__":
    print(calculate_score())