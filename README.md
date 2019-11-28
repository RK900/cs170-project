# CS170 Fall 2019 Project
The problem statement is, given a graph, start at source, drop a list of students at specific vertices, and return to destination.

The full spec: https://cs170.org/assets/project/spec.pdf

We attempted to solve the NP-hard similiar to Traveling salesman using linear programming.

## Creating Custom Inputs/Outputs 
We generate inputs and outputs randomly. Then, we place the TA locations randomly through the graph.
We run a solver through the nodes and time it. The graphs that take the longest to solve are the ones provided as input.

## Linear Programming Approach
We aim to solve the problem mainly through integer linear programming. We use the following given components of our lp: shortest path between all nodes and the distance between vertex i and j.

We define the variable x[i][j] as an indicator variable to be 1 if the car takes the route and 0 if the car doesn't take the route. Since we want to make sure that the source vertex makes a round trip we ensure that for each vertex the sum of x[i][j] of incoming + outgoing is an even number

To handle Ta walking home we define Ta[i][b] as an indicator variable  to be if the ta was dropped off at that vertex with 1 = dropped of at vertex 0 if not. To verify that each Ta goes home we constraint the sum of each Ta[i] == 1.

As we were building our lp, we realized that we could be creating invalid subtours. Then, we got inspired by the idea of flow to verify that each tour is connected to source. We define C as an integer that reprsents the amount of flow on a node. We say that flow in = flow out if its a node where a TA is dropped off. If a ta is dropped off, flow in - flow out = num ta dropped off. This is prevent local cycles that discount flow. We set the flow flowing out of source to be total flow, which is the number of Ta's to drop off. This idea was inspired by Single Commodity Flow.

Our objective function to minimze energy: 
![equation](https://latex.codecogs.com/gif.latex?%5Cmin%20%5Cfrac%7B2%7D%7B3%7D%20*%20%5Csum_%7B%28u%2Cv%29%20%5Cin%20Edges%7D%20x_%7Bu%2Cv%7D%20*%20Distance%28u%2Cv%29%20&plus;%201%20*%20%5Csum_%7Bi%20%5Cin%20TA%7D%20%5Csum_%7Bv%20%5Cin%20V%7D%20T%5Bi%5D%5Bv%5D%20*%20ShortestPath%28v%2C%20i%29)
<!-- Latex above is the rul encoded form of the below -->
<!-- encode at https://www.codecogs.com/latex/eqneditor.php and render image at https://latex.codecogs.com/gif.latex? -->
<!-- \min \frac{2}{3} * \sum_{(u,v) \forall edges} x_{ij} * d_{ij} + 1 * \sum_{i \in TA} \sum_{v \in V} T[i][v] * ShortestPath(v, i) -->


# Running the Code

## Setting up your environment
Create a virtualenv in python and install the requirements using the following command
```sh
pip3 install -r requirements.txt
```

## Choosing a LP solver
There are two solvers that you can use while running the project.

You can either use the open source CBC lp optimizer or the gurobi optimizer.

The gurobi optimizer is a commercial product that is given free for academic use. 
If you wish to use this optimizer, please go to the website and sign up for an account and active your gurobi account and license.

We noticed that gurobi was much faster than the CBC version especially for size 200 inputs.
## Running the solver
The solver can be run inside input_generator

Add the function that you want to run inside __main__ function at the bottom. We plan to move this to accept command line arguments later/moving it to another file.
### Running a single input file:
Update input_generator.py with the input_file.

The functions you can run are:
```python
def run(args):
    """
    input_file: path
        path to .in file specified in the spec
    draw: bool
        draws the result in a networkx graph
    output_path: path
        Saves the output of the solver to the specified output file
    output_log_path: path
        logs the upper and lower bounds of lp to file
    solver_mode: str
        "CBC" if you are using the open source solver. 
        "GRB" if you have gurobi installed on the computer
    """
```

The fastest way to run the code is below. It will display the optimal path with the variables that are set.
```python
if __name__ == '__main__':
    run('/path/to/store/output/<name>.out')
```

### Running Batch Function
The same idea as before but we allow for file ranges and extension types.
The following will run all the inputs in phase2 from range [1,5] with extensions 50,100,200 with time_limit 2 hours and 46 seconds

```python
if __name__ == '__main__':
    run_batch_inputs('input folder of .in files', file_range=[1, 5], extensions=['50','100','200'], solver_mode='GRB', time_limit=10000, output_folder="phase2_outputs", log_folder="phase2_log")
```

### Computation used
We used the CSUA latte server for most of our computation for size 200 inputs. We used our own laptops for 100 inputs.
