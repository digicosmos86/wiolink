#!/bin/bash

# Run this script only once after SSH into container

# Check if the micropython folder exists
if [ ! -d ~/micropython ] ; then
    cd ~
    git clone https://github.com/micropython/micropython.git ~/micropython --recurse-submodules
    cd ~/wiolink
fi

cd ~/micropython
make -C mpy-cross

cd ~/wiolink