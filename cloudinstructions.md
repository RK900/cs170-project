# 
sudo apt-get update
sudo apt-get install python3 python3-pip virtualenv tmux
wget https://packages.gurobi.com/9.0/gurobi9.0.0_linux64.tar.gz
tar xzvf gurobi9.0.0_linux64.tar.gz
touch ".bashrc"
echo 'export GUROBI_HOME="/home/$(whoami)/gurobi900/linux64"' >> ".bashrc"
echo 'export PATH="${PATH}:${GUROBI_HOME}/bin"' >> ".bashrc"
echo 'export LD_LIBRARY_PATH="${LD_LIBRARY_PATH}:${GUROBI_HOME}/lib"' >> ".bashrc"
echo 'export GRB_LICENSE_FILE="/home/$(whoami)/gurobi.lic"' >> ".bashrc"
source .bashrc


python3 parse_grb_probe.py <insert key here>

# logout and login again to get key
# can only be run on a url that already has it
# inside your project sudo virtualenv venv --python=python3 and then run tmux session
