#!/usr/bin/env python3
# Author: Ishwinder Singh(isingh176)
import subprocess, sys
import argparse



'''
OPS445 Assignment 2
Program: duim.py 
Author: "Ishwinder Singh"
The python code in this file (duim.py) is original work written by
"Ishwinder Singh". No code in this file is copied from any other source 
except those provided by the course instructor, including any person, 
textbook, or on-line resource. I have not shared this python script 
with anyone or anything except for submission for grading.  
I understand that the Academic Honesty Policy will be enforced and 
violators will be reported and appropriate action will be taken.

Description: This script calculates and displays disk usage of directories with optional bar graphs
and human-readable formats using the du command.

Date: 12/8/2024 
'''

def parse_command_args():
    '''Set up argparse here. Call this function inside main.
       This function handles command-line argument parsing'''
    parser = argparse.ArgumentParser(description="DU Improved -- See Disk Usage Report with bar charts",epilog="Copyright 2023")
    parser.add_argument("-l", "--length", type=int, default=20, help="Specify the length of the graph. Default is 20.")   # Argument for specifying the length of the bar graph
    # add argument for "human-readable". USE -H, don't use -h! -h is reserved for --help which is created automatically.
    parser.add_argument("-H", "--human-readable", action="store_true",   # Argument for human-readable format
                        help="Print sizes in human-readable format (e.g., 1K 23M 2G).")
    parser.add_argument("target", nargs="?", default=".",   # Argument for the target directory to scan, default set to current directory
                        help="The directory to scan. Defaults to current directory.")
    # check the docs for an argparse option to store this as a boolean.
    # add argument for "target". set number of args to 1.
    args = parser.parse_args()
    return args


def percent_to_graph(percent: int, total_chars: int) -> str:
    """Returns a string bar graph for a percentage."""
    if not (0 <= percent <= 100):   # Ensure the percent value is between 0 and 100
        raise ValueError("Percent must be between 0 and 100.")
    filled_chars = int(round(percent * total_chars / 100))   # Calculate the number of characters to fill based on the percentage
    return "=" * filled_chars + " " * (total_chars - filled_chars)   # Return a string with filled characters and spaces

def call_du_sub(location: str) -> list:
    """Use subprocess to call `du -d 1 + location`, return raw list."""
    try:
        result = subprocess.check_output(["du", "-d", "1", location], text=True, stderr=subprocess.PIPE)   # Run the `du` command with depth 1 on the specified location, capturing the output
        return result.strip().split("\n")   # Split the output into a list of lines and return it
    except subprocess.CalledProcessError as e:   # Handle errors that occur during the subprocess call
        # Filter out permission denied errors from stderr
        error_message = e.stderr if e.stderr else str(e)   # Retrieve the error message from stderr, or use the exception's string if stderr is not available
        if "Permission denied" in error_message:   # Check if the error is a permission denied error
            sys.stderr.write(f"Warning: Permission denied errors encountered.\n")   # Print a warning message to stderr if permission denied error
            return []
        else:
            sys.stderr.write(f"Error running du command: {error_message}\n")   # Print an error message to stderr and exit if other errors occur
            sys.exit(1)

def create_dir_dict(raw_dat: list) -> dict:
    "get list from du_sub, return dict {'directory': 0} where 0 is size"
    dir_dict = {}   # Initialize an empty dictionary to store directory sizes
    for line in raw_dat:   # Iterate through each line in the raw data list
        size, path = line.split(maxsplit=1)   # Split each line into size and path at the first space
        dir_dict[path] = int(size)   # Convert the size to an integer and store it in the dictionary with the path as the key 
    return dir_dict   # Return the dictionary containing directory paths and their corresponding sizes

def bytes_to_human_r(kibibytes: int, decimal_places: int=2) -> str:
    "turn 1,024 into 1 MiB, for example"
    suffixes = ['KiB', 'MiB', 'GiB', 'TiB', 'PiB']  # iB indicates 1024, List of suffixes representing different scales of byte units
    suf_count = 0   # Initialize the suffix count
    result = kibibytes   # Start with the given kibibytes value
    while result > 1024 and suf_count < len(suffixes):   # Convert the kibibytes value to the appropriate human-readable format
        result /= 1024
        suf_count += 1
    str_result = f'{result:.{decimal_places}f} '   # Format the result to the specified number of decimal places and add the appropriate suffix
    str_result += suffixes[suf_count]
    return str_result   # Return the formatted human-readable string

if __name__ == "__main__":
    args = parse_command_args()   # Parse the command-line arguments
    # Call du and get data
    du_output = call_du_sub(args.target)   # Call du and get disk usage data for the target directory
    dir_data = create_dir_dict(du_output)   # Create a dictionary from the raw du output data

    # Calculate total size
    total_size = sum(dir_data.values())

    # Print formatted output
    print(f"Disk usage for: {args.target}")
    for path, size in dir_data.items():   # Iterate over each directory and its size in the dictionary
        percent = (size / total_size) * 100 if total_size else 0   # Calculate the percentage of the total size for the current directory
        bar = percent_to_graph(percent, args.length)   # Generate a bar graph representation of the percentage
        size_display = bytes_to_human_r(size // 1024) if args.human_readable else f"{size}B"   # Format the size for display based on the human-readable flag
        print(f"{percent:.0f}% [{bar}] {size_display} {path}")   # Print the formatted output for the current directory

    # Print total
    total_display = bytes_to_human_r(total_size // 1024) if args.human_readable else f"{total_size}B"
    print(f"Total: {total_display}")

