#!/usr/bin/python3
import os

import subprocess
import threading

semaphore = threading.Semaphore(2)

with open('1-100.csv', 'r') as file:
    numbers = [int(line.strip()) for line in file]

    numbers = subprocess.run(["./calc.sh", numbers])
