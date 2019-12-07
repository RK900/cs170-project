import os
import sys
from student_utils import *
import calc_output
import multiprocessing as mp
pool = mp.Pool(mp.cpu_count())
outputs = sorted(os.listdir('phase2_outputs/'))
estimated_score = 0
num_inputs = len(outputs)
results = pool.map(calc_output.calc_output_file_ratio, outputs)
pool.close()
print(sum(results)/num_inputs * 100)
