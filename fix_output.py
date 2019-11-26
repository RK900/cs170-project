from output_validator import validate_output
def fix_output(input_file_name, validate=False,full_path=False):
    path = "phase2_outputs/{}.out".format(input_file_name)
    if full_path:
        path = input_file_name
    with open(path, 'r') as f:
        content = f.readlines()
    
    old_route = content[0][:]
    old_route = old_route.split()

    if old_route[0] == old_route[-1]:
        print(input_file_name, "already fixed")
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
        # print(new_route)
    

    print(' '.join(new_route))
    content[0] = ' '.join(new_route) + '\n'
    with open("phase2_outputs/{}.out".format(input_file_name), 'w') as f:
        f.writelines(content)
    
    if validate:
        with open("phase2_log/{}-log.out".format(input_file_name), 'r') as f:
            content = f.readlines()
            print(content)

        input_file, output_file = "phase2_inputs/{}.in".format(input_file_name), "phase2_outputs/{}.out".format(input_file_name)
        validate_output(input_file, output_file, params=[])


if __name__ == '__main__':
    fix_output('146_50')
