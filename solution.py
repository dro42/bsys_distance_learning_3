#!/usr/bin/python3
import os

import subprocess
import threading
from concurrent.futures import ThreadPoolExecutor

SEMAPHORE = threading.Semaphore(2)


# Saving generator output to a list
def slow_sort_with_threading(executor: ThreadPoolExecutor, list_to_be_sorted: list, start_index: int, end_index: int,
                             max_depth: int = 3, current_depth: int = 0):
    '''

    :param executor:
    :param list_to_be_sorted:
    :param start_index:
    :param end_index:
    :param max_depth:
    :param current_depth:
    :return:
    '''
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
    read file
    :param file_path: name of file
    :return: list of lines
    '''
    with open(file_path, 'r') as file:
        numbers = [int(line.strip()) for line in file]
    return numbers


def write_file(file_path: str, lines: list) -> None:
    '''
    write file
    :param lines: list of lines that needs to be written
    :param file_path: name of the file
    :return:
    '''
    if os.path.isfile(file_path):
        with open(file_path, 'w') as file:
            file.write(lines)
    else:
        with open(file_path, 'x') as file:
            file.write(lines)


# numbers = subprocess.run(["./calc.sh", numbers], capture_output=True, text=True)

# slow_sort_with_threading(ThreadPoolExecutor, numbers, 0, len(numbers) - 1)


def main():
    '''
    main function
    :return:
    '''
    file_list_old = [f"{i}-{i + 99}.csv" for i in range(1, 601, 100)]
    file_list_new = [f"{i}-{(i + 198)}.csv" for i in range(2, 1200, 200)]
    lines_new = []

    for i in range(len(file_list_old)):
        lines = read_file(file_list_old[i])
        lines_new.append(
            subprocess.run(["./calc.sh", lines], shell=True, stdout=subprocess.PIPE).stdout.decode('utf-8'))
        write_file(file_list_new[i], lines_new)

    print(file_list_old)
    print(file_list_new)


if __name__ == '__main__':
    main()
