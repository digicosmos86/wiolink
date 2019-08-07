#!/bin/bash

rm -rf ~/micropython
git clone https://github.com/micropython/micropython.git ~/micropython --recurse-submodules
cd ~/wiolink
cp -r umqtt ~/micropython/ports/esp8266/modules
rm ~/micropython/ports/esp8266/modules/inisetup.py
cp {wio_link,ssd1306,tsl2561,sensors,actuators,displays,urequests,inisetup,iot}.py ~/micropython/ports/esp8266/modules
#rm ~/micropython/ports/esp8266/modules/{dht,ds18x20,onewire,upip,upip_utarfile}.py
#cp ~/micropython/drivers/dht/dht.py micropython/ports/esp8266/modules/dht.py
#cp ~/micropython/drivers/onewire/{ds18x20,onewire}.py micropython/ports/esp8266/modules
#cp micropython/tools/{upip,upip_utarfile}.py micropython/ports/esp8266/modules
mkdir ~/micropython/ports/esp8266/scripts
cp boot.py ~/micropython/ports/esp8266/scripts
rm -f ~/micropython/ports/esp8266/scripts/main.py
cd ~/micropython
make -C mpy-cross
cp mpy-cross/mpy-cross  /home/esp/esp-open-sdk/xtensa-lx106-elf/bin/
cd ports/esp8266
#make axtls
make
rm -f ~/wiolink/micropython-1.9.3-wiolink-clean.bin
cp build/firmware-combined.bin ~/wiolink/micropython-1.9.3-wiolink-clean.bin