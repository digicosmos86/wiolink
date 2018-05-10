import network
import time
import urequests

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

    def send_http(self, url, data, https=False):
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
        except:
            print("Please check your url: {0}".format(address))

    def __repr__(self):
        return "Node-RED at {0}:{1}".format(self.ip, self.port)
        