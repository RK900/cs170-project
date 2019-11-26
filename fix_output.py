
def fix_output(input_file):
    with open(input_file, 'r') as f:
        content = f.readlines()
    
    old_route = content[0][:]
    old_route = old_route.split()

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
    with open(input_file, 'w') as f:
        f.writelines(content)


if __name__ == '__main__':
    fix_output('phase2_outputs/180_100.out')

