#!/usr/bin/python3
"""Importing needed modules for threading, triggering bash scripts and linux commands"""
import os
import subprocess
import sys
import threading

# Global semaphore to control the concurrent execution of the calc.sh script
SEMAPHORE = threading.Semaphore(2)


def slow_sort_with_threading(unsorted_list, start,
                             end, max_depth=4, cur_depth=0) -> None:
    """
    A multithreaded implementation of the slowsort algorithm.

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

    if cur_depth < max_depth:
        thread1 = threading.Thread(target=slow_sort_with_threading,
                                   args=(unsorted_list, start, mid, max_depth, cur_depth + 1))
        thread2 = threading.Thread(target=slow_sort_with_threading,
                                   args=(unsorted_list, mid + 1, end, max_depth, cur_depth + 1))

        thread1.start()
        thread2.start()

        thread1.join()
        thread2.join()
    else:
        slow_sort_with_threading(unsorted_list, start, mid, max_depth, cur_depth + 1)
        slow_sort_with_threading(unsorted_list, mid + 1, end, max_depth, cur_depth + 1)

    if unsorted_list[end] < unsorted_list[mid]:
        unsorted_list[end], unsorted_list[mid] = \
            (unsorted_list[mid], unsorted_list[end])

    slow_sort_with_threading(unsorted_list, start, end - 1, max_depth, cur_depth + 1)


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


def change_file_permissions(file_path, permissions=0o600) -> None:
    """
    Changes the permissions of a file.

    Args:
        file_path (str): Path to the file for which permissions will be changed.
        permissions (int): Unix file permissions to be set.
    """
    os.chmod(file_path, permissions)


def main() -> None:
    """
    Main function to process files. It reads numbers from old files,
    multiplies them using a Bash script, and writes the results to new files.
    """
    file_list_old = [f"{i}-{i + 99}.csv" for i in range(1, 601, 100)]
    file_list_new = [f"{i}-{i + 198}.csv" for i in range(2, 1200, 200)]

    for old_file, new_file in zip(file_list_old, file_list_new):
        lines = read_file(old_file)
        lines_new = []
        for line in lines:
            with SEMAPHORE:
                try:
                    result = subprocess.run(["./calc.sh", str(line)],
                                            capture_output=True, text=True, check=True)
                except subprocess.CalledProcessError as p_error:
                    print(f'An error occurred: {p_error}')
                if result.returncode == 0:
                    lines_new.append(int(result.stdout.strip()))
                else:
                    print(f"Error processing line {line}: {result.stderr.strip()}")
        # important to sort int not string otherwise sort is not correct
        slow_sort_with_threading(lines_new, 0, len(lines_new) - 1)
        write_file(new_file, lines_new)
        change_file_permissions(new_file)

    sys.exit(0)


if __name__ == '__main__':
    main()
