import re
import urequests
from iot import WiFi


def initWiFi(ssid, password):
    wifi = WiFi(ssid, password)
    wifi.connect()
    


def logData(token, key, value, url):
    
    thedata = {"token": token, "key": key, "value": value}
    
    response = urequests.request(method = 'POST', url = url, data = None, json = thedata)
    
    response.close()
