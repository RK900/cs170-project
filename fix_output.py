"""
Implementation of Hierholzer's algorithm to calculate eulerian path given a dfs
traversal. 

This stitches the closed parts of the loops together
"""

from output_validator import validate_output

def run_hierholzer(input_file_name, validate=False,full_path=False, output_folder="phase2_outputs", log_folder="phase2_log", input_folder="phase2_inputs"):
    path = "{}/{}.out".format(output_folder, input_file_name)
    if full_path:
        path = input_file_name
    with open(path, 'r') as f:
        content = f.readlines()
    
    old_route = content[0][:]
    old_route = old_route.split()

    if old_route[0] == old_route[-1]:
        print(input_file_name, "already fixed output")
        return
    
    new_route =  [old_route[0]]
    source = new_route[0]
    path_set = set()
    path_set.add(source)

    i = 1
    while old_route[i] != source:
        new_route.append(old_route[i])
        path_set.add(old_route[i])
        i += 1
    
    new_route.append(old_route[i]) # Add the source at the end
    i += 1

    while i < len(old_route):
        local_cycle = []
        ended = False
        while not ended and i < len(old_route) and old_route[i] != '\n':
            local_cycle.append(old_route[i])
            i += 1
            if local_cycle[-1] in path_set:
                ended = True
        
        ins = new_route.index(local_cycle[-1]) # Insert 1 elem after this

        new_route = new_route[:ins+1] + local_cycle + new_route[ins+1:]
        path_set.update(local_cycle)
    

    print(' '.join(new_route))
    content[0] = ' '.join(new_route) + '\n'
    with open(path, 'w') as f:
        f.writelines(content)
    
    if validate:
        with open("{}/{}-log.out".format(log_folder, input_file_name), 'r') as f:
            content = f.readlines()
            print(content)

        input_file, output_file = "{}/{}.in".format(input_folder, input_file_name), "{}/{}.out".format(output_folder, input_file_name)
        validate_output(input_file, output_file, params=[])


if __name__ == '__main__':
    run_hierholzer('324_200', validate=True)
