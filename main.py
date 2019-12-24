import click
from click import HelpFormatter, wrap_text
from click._compat import term_len
from colorama import init
from termcolor import colored
from analyze_logs import analyze_log
from calculate_score import calculate_score
from command_utils import title_header, PythonLiteralOption
from compress_output import compress_ouput
from graph_output import graph_output
from fix_output import run_hierholzer
from parse_grb_probe import print_grb_url
from output_validator import validate_output, validate_all_outputs
from input_generator import run_batch_inputs

@click.group()
@title_header(art=r"""
.______   .___  ___.    __    _  _    
|   _  \  |   \/   |   / /   | || |   
|  |_)  | |  \  /  |  / /_   | || |_  
|   _  <  |  |\/|  | | '_ \  |__   _| 
|  |_)  | |  |  |  | | (_) |    | |   
|______/  |__|  |__|  \___/     |_|   
                                      """)
def cli():
    # art created using https://onlineasciitools.com/convert-text-to-ascii-art
    pass

@cli.command()
@click.option('--extensions', cls=PythonLiteralOption, default='["50", "100","200"]') # Pass in list using --extension '["50", "100","200"]'
@click.option('--input-range', cls=PythonLiteralOption, default='[1,1]')      # Pass in list using --extension ["some option", "some option 2"]
@click.option('--input-folder', default="phase2_inputs/")
@click.option('--output-folder', default="phase2_outputs/")
@click.option('--log-folder', default="phase2_logs/")
@click.option('--solver-mode', default="GRB")
@click.option('--time-limit', default=50000)
def run_batch(extensions, input_range, input_folder, output_folder, log_folder, solver_mode, time_limit):
    """
    Run batch input
    """
    click.echo('running batch')
    run_batch_inputs(file_range=input_range, extensions=extensions,time_limit=time_limit, input_folder=input_folder, output_folder=output_folder, solver_mode=solver_mode, log_folder=log_folder)

@cli.command()
@click.option('--filename', default="outputs.json")
@click.option('--folder', default="phase2_outputs/")
def compress_output_folder(filename, folder):
    """
    Compress output folder to outputs.json
    """
    click.echo('Compress Output')
    compress_ouput(filename, folder)

@cli.command()
@click.option('--input-folder', default="phase2_inputs/")
@click.option('--output-folder', default="phase2_outputs/")
def calc_score(input_folder, output_folder):
    """
    Calculate score based on ratio
    """
    click.echo('Calculating Score')
    calculate_score(input_folder, output_folder)

@cli.command()
@click.option('--input-file', default="phase2_inputs/")
@click.option('--output-file', default="phase2_outputs/")
def validate_output_file(input_file, output_file):
    """
    Validate output file
    """
    click.echo('Validate output')    
    input_validator.VALID_FILENAMES.append(input_file)
    validate_output(input_file, output_file, params=[])

@cli.command()
@click.option('--input-folder', default="phase2_inputs/")
@click.option('--output-folder', default="phase2_outputs/")
def validate_all(input_folder, output_folder):
    """
    Validate all outputs
    """
    click.echo('Validate all outputs')
    input_validator.VALID_FILENAMES.append(input_folder)
    validate_all_outputs(input_folder, output_folder, params=[])

@cli.command()
@click.option('--key', default="<key>")
def get_grb_url(key):
    """
    Gets the gurobi url for machine with gurobi
    """
    click.echo('Grb Probe Url')
    print_grb_url(key)

@cli.command()
@click.option('--output-file', default="tests/output/10_50.in")
def graph_output(output_file):
    """
    Graph the output file path
    """
    click.echo('graph_output')
    graph_output(output_file)

@cli.command()
@click.option('--log-folder', default="phase2_log")
@click.option('--error', default=0.001, help='The min error between bound to consider')
def analyze_logs(log_folder,error):
    """
    Analyze Log folder within err based on diff between bound and actual
    """
    click.echo('Analyzing Logs')
    analyze_log("phase2_log", error)

@cli.command()
@click.option('--output-file', default="tests/output/10_50.in")
def run_hierholzer(output_file):
    """
    Fixes dfs output so that paths start and end at the same spot
    """
    click.echo('Run run_hierholzer on a input')
    run_hierholzer(output_file)

if __name__ == '__main__':
    cli()