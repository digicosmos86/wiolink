cd micropython/ports/esp8266
make clean
cd ~/wiolink
cd micropython
git submodule update --init
cd ports/esp8266
make axtls
cd ~/wiolink
cp -r umqtt micropython/ports/esp8266/modules
cp {wio_link,ssd1306,tsl2561,sensors,actuators,displays,urequests}.py micropython/ports/esp8266/modules
cp {boot,main}.py micropython/ports/esp8266/scripts
cd micropython/ports/esp8266
make
cp ./build/firmware-combined.bin /vagrant/micropython-1.9.3-wiolink-preprogram.bin