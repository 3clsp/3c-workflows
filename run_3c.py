import os
import logging
import subprocess
import sys
import shutil
from colorama import Fore, Style

EDK2_PATH = "/edk2"
BUILD_PATH = f"{EDK2_PATH}/Build"
BASE_CMD = "OvmfPkg/build.sh -t CLANGPDB".split(" ")
OUT_PATH = "/checkedc-llvm-project/clang/tools/3c/utils/port_tools/jsons"
RUN_PATH = "/checkedc-llvm-project/clang/tools/3c/utils/port_tools/"
THREEC_BIN = "/checkedc-llvm-project/build/bin/3c" 
FAILED_PATH = "/checkedc-llvm-project/clang/tools/3c/utils/port_tools/failed"

clean = False
build = False

def do_work(compile_commands, path, patho, with_itypes=False):
    # Copy the compile_commands.json to the edk2 root
    shutil.copy(file, EDK2_PATH)
    os.chdir(RUN_PATH)

    # Run 3c
    args = ["python3", "convert_project.py", "-pr", EDK2_PATH, "-p", THREEC_BIN, "--extra-3c-arg", "'-alltypes'", "--extra-3c-arg", "'--allow-rewrite-failures'"]
    if with_itypes:
        args.extend(["--extra-3c-arg", "'--infer-types-for-undefs'"])
    
    output = subprocess.run(args)
    if output.returncode != 0:
        print(f"{Fore.RED}3c failed")
        print(Style.RESET_ALL)
        path = FAILED_PATH + patho
        os.makedirs(path, exist_ok=True)
        # Save the failed compile commands
        shutil.copy(file, path)
    else:
        print(f"{Fore.GREEN}3c succeeded")
        print(Style.RESET_ALL)
        # Check if the run path has any json files
        jsons = os.listdir(RUN_PATH)
        json_files_exist = any(f.endswith(".json") for f in jsons)
        if not json_files_exist:
            print(f"{Fore.RED}No json files found")
            print(Style.RESET_ALL)
        else:
            # Since we run 3c two times per module, we need to rename the json files
            path_files = os.listdir(path)
            path_json_files_exist = any(f.endswith(".json") for f in path_files)
            if path_json_files_exist:
                print(f"{Fore.WHITE}Json files already exist in the output directory")
                print(Style.RESET_ALL)
                for json in path_files:
                    if json.endswith(".json"):
                        os.rename(f"{path}/{json}", f"{path}/{json}.without_itypes")

            # Move the json files to the output directory
            for json in jsons:
                if json.endswith(".json"):
                    shutil.move(json, path)


if len(sys.argv) > 1:
    if "clean" in sys.argv:
        clean = True
    if "build" in sys.argv:
        build = True
    if "help" in sys.argv:
        print("Usage: python3 build.py [clean] [build] [help]")
        print("clean: Remove existing build directory")
        print("build: Build the project")
        print("help: Print this message")
        exit(0)
else:
    print("No arguments provided. Running 3c only")

# Make sure we are running it inside the docker container
if not os.path.exists(EDK2_PATH):
    logging.error("EDK2_PATH does not exist: %s", EDK2_PATH)
    logging.error("Are you running this inside the docker container?")
    exit(1)

os.chdir(EDK2_PATH)
# Only clean if the user wants to
if clean:
    # Remove existing build
    if os.path.exists(BUILD_PATH):
        logging.info("Removing Build directory")
        subprocess.run(["OvmfPkg/build.sh", "-t", "CLANGPDB", "clean"])
        subprocess.run(["rm", "-rf", BUILD_PATH])

if build:
    # Build the project
    logging.info("Building the project")
    output = subprocess.run(BASE_CMD)
    if output.returncode != 0:
        logging.error("Build failed")
        exit(1)

# Check if the build directory exists
if not os.path.exists(BUILD_PATH):
    logging.error("Build directory does not exist")
    logging.error("Are you sure you ran the build command?")
    exit(1)

# Collect all compile commands
output = subprocess.run(["find", BUILD_PATH, "-name", "compile_commands.json"], stdout=subprocess.PIPE)
if output.returncode != 0:
    logging.error("Failed to find compile_commands.json")
    exit(1)

# Print the output of above command
logging.info("compile_commands.json:")
files = output.stdout.decode("utf-8").strip()

for file in files.split("\n"):
    print(f"{Fore.YELLOW}Running 3c with compile_commands {file}")
    print(Style.RESET_ALL)
    patho = os.path.dirname(file)
    path = OUT_PATH + patho
    print(f"{Fore.YELLOW}Output path: {path}")
    os.makedirs(path, exist_ok=True)
    print(Style.RESET_ALL)
    
    # do_work(file, path, patho)
    do_work(file, path, patho, True)
    
    # Remove the compile_commands.json from the edk2 root
    os.remove(f"{EDK2_PATH}/compile_commands.json")
