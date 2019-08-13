#!/bin/bash

cd ~/micropython/ports/esp8266
git submodule update --init

cp -r ~/wiolink/modules/* ~/micropython/ports/esp8266/modules
rm -rf ~/micropython/ports/esp8266/modules/umqtt

if [ ! -d ~/micropython/ports/esp8266/scripts ] ; then
    rm -rf ~/micropython/ports/esp8266/scripts
fi

mkdir ~/micropython/ports/esp8266/scripts
cp ~/wiolink/scripts/boot.py ~/micropython/ports/esp8266/scripts/boot.py

make FLASH_SIZE=32m

if [ -d ~/wiolink/micropython-1.11-wiolink-clean.bin ] ; then
    rm ~/wiolink/micropython-1.11-wiolink-clean.bin
fi

cp ~/micropython/ports/esp8266/build/firmware-combined.bin ~/wiolink/build/micropython-1.11-wiolink-clean.bin