#!/usr/bin/python3
# created by Andreas Drozd CSDCBB26
"""Importing needed modules for threading, triggering bash scripts and linux commands"""
import os
import subprocess
import sys
import threading
from typing import Optional

# Global semaphore to control the concurrent execution of the calc.sh script
SEMAPHORE = threading.Semaphore(2)


def read_file(file_path) -> list:
    """
    Reads a file and returns its contents as a list of lines.

    Args:
        file_path (str): Path to the file to be read.

    Returns:
        list: List of lines in the file.
    """
    with open(file_path, 'r') as file:
        return [int(line.strip()) for line in file]


def write_file(file_path, lines) -> None:
    """
    Writes a list of lines to a file. If the file exists, it's overwritten;
    otherwise, a new file is created.

    Args:
        file_path (str): Path to the file to be written.
        lines (list): List of lines to write to the file.
    """
    mode = 'w' if os.path.isfile(file_path) else 'x'
    with open(file_path, mode) as file:
        for line in lines:
            file.writelines(f'{line}\n')


def calc_double(value: str) -> Optional[int]:
    """
    Calculate double of a given value using an external bash script.

    This function calls an external bash script ('calc.sh') to double the input value.
    It uses a semaphore to limit concurrent execution of the script.

    Args:
        value (str): The value to be doubled.

    Returns:
        int: The doubled value returned by the bash script.
        None: If an error occurs or the script fails.
    """
    with SEMAPHORE:
        try:
            result = subprocess.run(["./calc.sh", str(value)],
                                    capture_output=True, text=True, check=True)
            return int(result.stdout.strip())
        except subprocess.CalledProcessError as p_error:
            # Handle any errors that occur during the subprocess execution
            print(f'An error occurred: {p_error}')
            return None  # Explicitly return None in case of an error


def slow_sort_start(unsorted_list, start, end):
    """
        Doubles all the values in the list and then sorts the list using the slow_sort algorithm.

        Args:
            unsorted_list (list): The list to be sorted.
            start (int): Starting index of the segment of the list to be sorted.
            end (int): Ending index of the segment of the list to be sorted.
        """
    # Double each element in the list in place using list comprehension
    unsorted_list[:] = [calc_double(item) for item in unsorted_list]

    # Sort the list using the slow sort algorithm
    slow_sort(unsorted_list, start, end)


def slow_sort(unsorted_list, start,
              end) -> None:
    """
    A multithreading implementation of the slow sort algorithm.

    Args:
        unsorted_list (list): The list to be sorted.
        start (int): Starting index of the segment of the list to be sorted.
        end (int): Ending index of the segment of the list to be sorted.
        max_depth (int): Maximum depth to create new threads for sorting.
        cur_depth (int): Current depth in the recursion tree.
    """
    if start >= end:
        return

    mid = (start + end) // 2

    slow_sort(unsorted_list, start, mid)
    slow_sort(unsorted_list, mid + 1, end)

    if unsorted_list[end] < unsorted_list[mid]:
        unsorted_list[end], unsorted_list[mid] = \
            (unsorted_list[mid], unsorted_list[end])

    slow_sort(unsorted_list, start, end - 1)


def change_file_permissions(file_path, permissions=0o600) -> None:
    """
    Changes the permissions of a file.

    Args:
        file_path (str): Path to the file for which permissions will be changed.
        permissions (int): Unix file permissions to be set.
    """
    os.chmod(file_path, permissions)


def process_file(old_file, new_file):
    """
    Function to process a single file: read, sort, write, and change permissions.

    Args:
        old_file (str): The path to the file to be read.
        new_file (str): The path to the file where results will be written.
    """
    lines = read_file(old_file)
    slow_sort_start(lines, 0, len(lines) - 1)
    write_file(new_file, lines)
    change_file_permissions(new_file)


def main() -> None:
    """
    Main function to process files. It reads numbers from old files,
    multiplies them using a Bash script, and writes the results to new files.
    """
    file_list_old = [f"{i}-{i + 99}.csv" for i in range(1, 601, 100)]
    file_list_new = [f"{i}-{i + 198}.csv" for i in range(2, 1200, 200)]

    # Create threads using generator expression
    threads = (threading.Thread(target=process_file, args=(old_file, new_file))
               for old_file, new_file in zip(file_list_old, file_list_new))

    # Start threads
    for thread in threads:
        thread.start()

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

    sys.exit(0)


if __name__ == '__main__':
    main()
