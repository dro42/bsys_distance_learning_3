#!/usr/bin/python3
import os
import subprocess
import threading
from concurrent.futures import ThreadPoolExecutor

# Global semaphore to control the concurrent execution of the calc.sh script
SEMAPHORE = threading.Semaphore(2)


def slow_sort_with_threading(executor: ThreadPoolExecutor, list_to_be_sorted: list, start_index: int, end_index: int,
                             max_depth: int = 4, current_depth: int = 0):
    if start_index >= end_index:
        return  # Base case: if the range is empty or invalid, do nothing

    middle_index = (start_index + end_index) // 2  # Calculate the middle index

    if current_depth < max_depth:
        # Recursively sort the two halves of the list in separate threads
        future1 = executor.submit(slow_sort_with_threading, executor, list_to_be_sorted, start_index, middle_index,
                                  max_depth, current_depth + 1)
        future2 = executor.submit(slow_sort_with_threading, executor, list_to_be_sorted, middle_index + 1, end_index,
                                  max_depth, current_depth + 1)

        # Wait for both halves to be sorted
        future1.result()
        future2.result()
    else:
        # Perform the sorting in the current thread without creating new threads
        slow_sort_with_threading(executor, list_to_be_sorted, start_index, middle_index, max_depth, current_depth + 1)
        slow_sort_with_threading(executor, list_to_be_sorted, middle_index + 1, end_index, max_depth, current_depth + 1)

    # Perform the conditional swap
    if list_to_be_sorted[end_index] < list_to_be_sorted[middle_index]:
        list_to_be_sorted[end_index], list_to_be_sorted[middle_index] = list_to_be_sorted[middle_index], \
            list_to_be_sorted[end_index]

    # Recursively sort the list again, excluding the last element
    slow_sort_with_threading(executor, list_to_be_sorted, start_index, end_index - 1, max_depth, current_depth + 1)


def read_file(file_path: str) -> list:
    '''
    Reads a file and returns its contents as a list of lines.

    :param file_path: Path to the file to be read.
    :return: List of lines in the file.
    '''
    with open(file_path, 'r') as file:
        numbers = [int(line.strip()) for line in file]
    return numbers


def write_file(file_path: str, lines: list) -> None:
    '''
    Writes a list of lines to a file. If the file exists, it's overwritten;
    otherwise, a new file is created.

    :param file_path: Path to the file to be written.
    :param lines: List of lines to write to the file.
    '''
    mode = 'w' if os.path.isfile(file_path) else 'x'
    with open(file_path, mode) as file:
        for line in lines:
            file.write(line)


def change_file_permissions(file_path: str, permissions=0o600) -> None:
    '''
    Changes the permissions of a file.

    :param file_path: Path to the file for which permissions will be changed.
    :param permissions: Unix file permissions to be set.
    '''
    os.chmod(file_path, permissions)


def main():
    '''
    Main function to process files. It reads numbers from old files,
    multiplies them using a Bash script, and writes the results to new files.
    '''
    file_list_old = [f"{i}-{i + 99}.csv" for i in range(1, 601, 100)]
    file_list_new = [f"{i}-{(i + 198)}.csv" for i in range(2, 1200, 200)]

    for old_file, new_file in zip(file_list_old, file_list_new):
        lines = read_file(old_file)
        lines_new = []
        for line in lines:
            # Using the semaphore to limit concurrent executions of the script
            with SEMAPHORE:
                result = subprocess.run(["./calc.sh", f'{line}'], capture_output=True, text=True)
                if result.returncode == 0:
                    lines_new.append(result.stdout.strip() + "\n")
                else:
                    print(f"Error processing line {line}: {result.stderr.strip()}")
        with SEMAPHORE:
            with ThreadPoolExecutor() as executor:
                slow_sort_with_threading(executor, lines_new, 0, len(lines_new) - 1)

        write_file(new_file, lines_new)
        change_file_permissions(new_file)


if __name__ == '__main__':
    main()
