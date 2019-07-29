import network
import time
import urequests
import re
from sensors import Sensor
from utime import ticks_ms

class WiFi:
    
    def __init__(self, ssid, password):
        self.ssid = ssid
        self.password = password
        self.wlan = network.WLAN(network.STA_IF)
        self.wlan.active(True)

    def connect(self):
        if not self.wlan.isconnected():
            for i in range(3, 0, -1):
                print('Connecting to network "{0}"'.format(self.ssid))
                self.wlan.connect(self.ssid, self.password)
                time.sleep(3)
                if self.wlan.isconnected():
                    print("\nConnection Successful!")
                    print("Network config:", self.wlan.ifconfig())
                    return
                else:
                    print("Connection unsuccessful. Retrying. {0} attempts left".format(i-1))

    def __repr__(self):
        return "WiFi object with SSID: {0}".format(self.ssid)


class NodeRed:

    def __init__(self, ip, port=1880):
        self.ip = ip
        self.port = port

    def send_http(self, url, data, https=False, debug=True):
        if url[0] != "/":
            url = "/" + url
        if https:
            address = "https://{0}:{1}{2}".format(self.ip, self.port, url)
        else:
            address = "http://{0}:{1}{2}".format(self.ip, self.port, url)
        try:
            if isinstance(data, dict):
                r = urequests.post(address, json=data)
            else:
                r = urequests.post(address, data=data)
            r.close()
            if debug:
                print("Data sent!")
        except OSError:
            print("Error! Please check your domain or IP address")
        except:
            print("Unknown error. Please check with an instructor.")

    def __repr__(self):
        return "Node-RED at {0}:{1}".format(self.ip, self.port)


class BcServer(NodeRed):
    
    def __init__(self, team):
        NodeRed.__init__(self, ip="ts.bc.edu", port=1880)
        self.data = { "team": team }
        self.last = None

    def send_http(self, data, debug=True):
        address = "http://{0}:{1}/data".format(self.ip, self.port)
        try:
            if isinstance(data, dict):
                r = urequests.post(address, json=data)
            else:
                r = urequests.post(address, data=data)
            r.close()
            if debug:
                print("Data sent!")
        except OSError:
            print("Error! Please check your domain or IP address")
        except:
            print("Unknown error. Please check with an instructor.")

    def send_sensor_data(self, sensor, debug=True):
        now = ticks_ms()
        if self.last is None or now - self.last >= 10000:
            if isinstance(sensor, list):
                for each_sensor in sensor:
                    self._sensor_to_data(each_sensor)
            else:
                self._sensor_to_data(sensor)
            
            self.send_http(data=self.data, debug=debug)
            self.last = ticks_ms()
        
    def _sensor_to_data(self, sensor):
        if not isinstance(sensor, Sensor):
            raise ValueError("One or more objects are not Sensors!")
        if sensor.type == "TempSensor":
            t, h = sensor.get_data()
            self.data["temperature"] = t
            self.data["humidity"] = h
        elif sensor.type == "MoistureSensor":
            self.data["soil"] = sensor.get_data()
        elif sensor.type == "LightSensor":
            self.data["lux"] = sensor.get_data()
        elif sensor.type == "WaterTempSensor":
            self.data["water temperature"] = sensor.get_data()
    
    def __repr__(self):
        return "BC Server at {0}:{1}".format(self.ip, self.port)