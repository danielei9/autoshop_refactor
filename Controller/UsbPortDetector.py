import re
import subprocess
import os
from os.path import join
import platform
# MONEDERO idvendor  067b


class USBPortDetector:
    def __init__(self):
        
        self.portBilletero = None
        self.portMonedero = None
        self.portDisplay = None
        self.portLeds = None

        if platform.system() == "Windows":
            print("El sistema operativo es Windows")
        elif platform.system() == "Linux":
            print("El sistema operativo es Linux")
        else:
            print("El sistema operativo desconocido es : " + str(platform.system()))
            assert("El sistema operativo es desconocido")

    def detect_ports(self):
        if platform.system() == "Windows":
            return ('COM1', 'COM2', 'COM3', 'COM4')
            return (None, None, None, None)
        elif platform.system() == "Linux":
            (self.portBilletero,self.portMonedero,self.portDisplay,self.portLeds) = self.checkPorts()
            return (self.portBilletero,self.portMonedero,self.portDisplay,self.portLeds)
        else:
            print("El sistema operativo es desconocido")
            assert("El sistema operativo es desconocido")
        pass

    def find_tty_usb(self,idVendor, idProduct):
        for dnbase in os.listdir('/sys/bus/usb/devices'):
            dn = join('/sys/bus/usb/devices', dnbase)
    #         print(dn)
            if not os.path.exists(join(dn, 'idVendor')):
                continue
            idv = open(join(dn, 'idVendor')).read().strip()
    #         print(idv)
            if idv != idVendor:
                continue
            idp = open(join(dn, 'idProduct')).read().strip()
    #         print(idp)
            if idp != idProduct:
                continue
            for subdir in os.listdir(dn):
                if subdir.startswith(dnbase+':'):
                    for subsubdir in os.listdir(join(dn, subdir)):
                        if subsubdir.startswith('ttyUSB'):
                            return join('/dev', subsubdir)
    def checkPorts(self):
        devices = []
        portBilletero = None
        portMonedero = None
        portDisplay = None
        portLeds = None
        
        device_re = re.compile("Bus\s+(?P<bus>\d+)\s+Device\s+(?P<device>\d+).+ID\s(?P<id>\w+:\w+)\s(?P<tag>.+)$", re.I)
        df = subprocess.check_output("lsusb")    
        df = str(df)
        df = df.replace("b'", '')
        for i in df.split("\\n"):
            if i:
                info = device_re.match(i)
                if info:
                    dinfo = info.groupdict()
                    dinfo['device'] = '/dev/bus/usb/%s/%s' % (dinfo.pop('bus'), dinfo.pop('device'))
                    devices.append(dinfo)
    #     print (devices)

        for device in devices:
            idUsb = str(device['id']).split(':')
            a = str(idUsb[0])
            b = str(idUsb[1])
            # print(device['id'])
        #     BILLETERO
        # Bus 001 Device 116: ID 067b:2303 Prolific Technology, Inc. PL2303 Serial Port
            if(device['id'] == "067b:2303"):
                portBilletero = self.find_tty_usb(a,b)
                print("BILLETERO: ",portBilletero,"\n")
        # Bus 001 Device 115: ID 0403:6001 Future Technology Devices International, Ltd FT232 Serial (UART) IC
        #     MONEDERO
            if(device['id'] == "0403:6001"):
                portMonedero = self.find_tty_usb(a,b) 
                print("MONEDERO: ",portMonedero,"\n")
        # Bus 001 Device 019: ID 10c4:ea60 Cygnal Integrated Products, Inc. CP2102/CP2109 UART Bridge Controller [CP210x family]
        #     DISPLAY
            if(device['id'] == "10c4:ea60"):
                portDisplay = self.find_tty_usb(a,b)
                print("DISPLAY: ",portDisplay,"\n")
        # Bus 001 Device 020: ID 1a86:7523 QinHeng Electronics HL-340 USB-Serial adapter
        #     LEDS
            if(device['id'] == "1a86:7523"):
                portLeds = self.find_tty_usb(a,b)
                print("LEDS: ",portLeds,"\n")
            
        return portBilletero,portMonedero,portDisplay,portLeds

