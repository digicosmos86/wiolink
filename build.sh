#!/bin/bash

rm -rf micropython
git submodule update -f --init
cd micropython
git submodule update -f --init
cd ..
cp -r umqtt micropython/ports/esp8266/modules
rm micropython/ports/esp8266/modules/inisetup.py
cp {wio_link,ssd1306,tsl2561,sensors,actuators,displays,urequests,inisetup,iot}.py micropython/ports/esp8266/modules
rm micropython/ports/esp8266/modules/{dht,ds18x20,onewire,upip,upip_utarfile}.py
cp micropython/drivers/dht/dht.py micropython/ports/esp8266/modules/dht.py
cp micropython/drivers/onewire/{ds18x20,onewire}.py micropython/ports/esp8266/modules
cp micropython/tools/{upip,upip_utarfile}.py micropython/ports/esp8266/modules
mkdir micropython/ports/esp8266/scripts
cp boot.py micropython/ports/esp8266/scripts
rm micropython/ports/esp8266/scripts/main.py
cd micropython/ports/esp8266
make axtls
make
rm ~/wiolink/micropython-1.9.3-wiolink-clean.bin
cp build/firmware-combined.bin ~/wiolink/micropython-1.9.3-wiolink-clean.bin