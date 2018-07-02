## Custom-built MicroPython Firmware for WioLink

This repository contains files used to build a custom MicroPython firmware for WioLink, a development board based on ESP8266 featuring 6 grove ports. This firmware was used in a smart greenhouse project for 200 8th Graders.

## How to use this repository

The easiest way to use this library is to use docker. Use the docker file used in this folder to create a docker image with the necessary toolchain compiled and ready to use (this might take approximately 20 minutes or longer for the image to be built). After the toolchain is built, mount the present working directory within the docker container, and run build.sh shell script. The script will download the MicroPython repo and build the MicroPython firmware, and the firmware will appear as a .bin file in the same folder. Once you've run build.sh, you can run quickbuild.sh to quickly build firmware in the future.
