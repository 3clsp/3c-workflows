FROM ubuntu:22.04

RUN apt-get update && \
    apt-get -y install git gcc bear g++ make uuid-dev \
    python-is-python3 build-essential nasm iasl libx11-dev \
    libxv-dev gdb gcc-aarch64-linux-gnu libncurses-dev \
    autoconf libssl-dev qemu-system-x86 clang llvm lld \
    python3-pip

RUN pip install colorama

CMD ["/bin/bash"]
