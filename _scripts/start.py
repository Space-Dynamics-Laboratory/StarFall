#!/usr/bin/env python3

################################################################################################
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
#################################################################################################

"""
This script runs multiple executables and prints the standout in a nice combined way.
See line 120 to specify the commands to run.

From the root of the project run

> python3 ./_scripts/start.py

"""

import multiprocessing
import subprocess
from queue import Queue, Empty
from threading import Thread
import re
import signal
import sys
from datetime import datetime

# global -- whether logging to file should be enabled
LogToFile = False


class ConsoleHelper:
    BLACK = "\033[30m"
    DARK_RED = "\033[31m"
    DARK_GREEN = "\033[32m"
    DARK_YELLOW = "\033[33m"
    DARK_BLUE = "\033[34m"
    DARK_MAGENTA = "\033[35m"
    DARK_CYAN = "\033[36m"
    DARK_GRAY = "\033[90m"
    LIGHT_GRAY = "\033[37m"
    LIGHT_RED = "\033[91m"
    LIGHT_GREEN = "\033[92m"
    LIGHT_YELLOW = "\033[93m"
    LIGHT_BLUE = "\033[94m"
    LIGHT_MAGENTA = "\033[95m"
    LIGHT_CYAN = "\033[96m"
    WHITE = "\033[97m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    ENDCOLOR = "\033[0m"


class Executable:
    def __init__(self, command, cwd, displayName, displayColor):
        self.command = command
        self.cwd = cwd
        self.displayName = displayName
        self.displayColor = displayColor
        self.process = None  # holds the process once launched
        self.thread = None  # holds the thread for monitoring output
        self.regex = re.compile(
            f"{self.displayName}" + r" (?P<command>.*)", re.IGNORECASE
        )
        global LogToFile
        if LogToFile:
            self.logFile = open(f"{displayName}.log", "w")

    def launch(self):
        self.process = subprocess.Popen(
            self.command,
            cwd=self.cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.PIPE,
            text=True,
        )

    def attachOutputToQueue(self, queue):
        self.thread = Thread(target=write_output, args=(self, queue), daemon=True)
        self.thread.start()

    def close(self):
        # # kill process
        self.process.terminate()
        self.process.wait(5)
        # join thread
        self.thread.join()
        # close log file
        global LogToFile
        if LogToFile:
            self.logFile.close()


def write_output(executable, queue):
    global LogToFile
    now = f'{datetime.now().strftime("%m/%d/%Y %H:%M:%S.%f")[:-3]}'
    try:
        for line in executable.process.stdout:
            if len(line) > 0:
                if LogToFile:
                    executable.logFile.write(f"{now} {line}")
                queue.put(
                    f"{executable.displayColor}{now} [{executable.displayName}] {line.rstrip()}{ConsoleHelper.ENDCOLOR}"
                )
        for line in executable.process.stderr:
            if len(line) > 0:
                if LogToFile:
                    executable.logFile.write(f"{now} {line}")
                queue.put(
                    f"{ConsoleHelper.DARK_RED}{ConsoleHelper.BOLD}{now} ERROR: [{executable.displayName}] {line.rstrip()}{ConsoleHelper.ENDCOLOR}"
                )
        if LogToFile:
            executable.logFile.flush()
    except:
        pass


def signal_handler(sig, frame):
    for executable in executables:
        executable.close()
    processesToKill = multiprocessing.active_children()
    for p in processesToKill:
        try:
            if p.is_alive():
                p.kill()
        except:
            pass
    sys.exit(0)


# Executables to launch
executables = [
    Executable(
        command=["npm", "run", "dev"],
        cwd="starfall-viewer",
        displayName="SV",
        displayColor=ConsoleHelper.LIGHT_CYAN,
    ),
    Executable(
        command=["npm", "run", "serve"],
        cwd="starfall-server",
        displayName="SS",
        displayColor=ConsoleHelper.DARK_YELLOW,
    ),
]

# attach CTRL+C signal handler
signal.signal(signal.SIGINT, signal_handler)

# Thread safe queue for interleaving messages
queue = Queue()


def printFromQueue(queue):
    while True:
        try:
            line = queue.get_nowait()
            print(line)
        except Empty:
            pass


consoleThread = Thread(target=printFromQueue, args=(queue,))
consoleThread.daemon = True
consoleThread.start()

# Launch executables
for executable in executables:
    executable.launch()
    executable.attachOutputToQueue(queue)


while True:
    userInput = input("")
    # Input for subprocess?
    for executable in executables:
        matches = executable.regex.search(userInput)
        if matches is not None:
            now = f'{datetime.now().strftime("%m/%d/%Y %H:%M:%S.%f")[:-3]}'
            command = matches.group("command")
            print(f"Sending command '{command}' -> {executable.displayName}")
            try:
                executable.process.stdin.write(command)
                executable.process.stdin.flush()
                for line in executable.process.stdin:
                    if len(line) > 0:
                        if LogToFile:
                            executable.logFile.write(f"{now} {line}")
                        queue.put(
                            f"{executable.displayColor}{now} [{executable.displayName}] {line.rstrip()}{ConsoleHelper.ENDCOLOR}"
                        )
            except:
                pass