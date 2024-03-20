import os
import subprocess

EDK2_PATH = "/edk2"
BUILD_PATH = f"{EDK2_PATH}/Build"


# Get the list of all the files
out = subprocess.run(["find", BUILD_PATH, "-name", "*compile_commands.json"], stdout=subprocess.PIPE)

files = out.stdout.decode("utf-8").strip().split("\n")

for file in files:
    out = ""
    text = open(file)
    line = text.readline()
    while line:
        if not "-DEFIAPI=__attribute__((ms_abi))" in line:
            out += line
        line = text.readline()
    print(out)
    text.close()
    # write back the file
    with open(file, "w") as f:
        f.write(out)
    # exit(0)