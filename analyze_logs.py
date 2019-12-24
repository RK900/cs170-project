"""
Analyze the logs to view the difference between objective bound 
"""
import os
import sys

def analyze_log(phase2_log, err=0.001):
    lst = []
    for item in os.listdir(f'{phase2_log}/'):
        with open(f'{phase2_log}/{item}','r') as f:
            lst.append(f.readlines() + [item])
    new_lst = [[float(item[0].split(": ")[1].strip()),float(item[1].split(": ")[1].strip()), item[2]] for item in lst]
    print("error bound {}".format(err))
    i = 0
    for item in new_lst:
        diff = abs((item[1] - item[0])/item[1])
        if diff > err:
            i += 1
            print(item[2], item[1], item[0], diff)
    print("{} items with error greater than {}".format(i, err))

if __name__ == "__main__":
    err = 0.001
    if len(sys.argv) >= 2:
        err = float(sys.argv[1])
    analyze_log("phase2_log", err)
