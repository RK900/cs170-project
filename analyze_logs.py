import os
lst = []
for item in os.listdir('phase2_log/'):
    with open('phase2_log/' + item,'r') as f:
        lst.append(f.readlines() + [item])
new_lst = [[float(item[0].split(": ")[1].strip()),float(item[1].split(": ")[1].strip()), item[2]] for item in lst]
err = 0.001
for item in new_lst:
    diff = abs((item[1] - item[0])/item[1])
    if diff > err:
        print(item[2], item[1], item[0], diff)