# -*- coding: utf-8 -*-
"""
 @Author: Daniel Burruchaga Sola
        @Date: 25-04-22

Example:
    portConfig = s.serialBegin(baudrate)  open the port

Todo:
    * Review some doc and 
    * Feature auto-select port

|--------BuchuSerial------|
|        __init__     setBaudrate()    
|        baudrate     serial_ports()
|                     serialBegin()
|                     serialWriteString(str)
|                     serialWrite()
|                     serialOpen()
|                     serialReadLine()
|                     serialxBytesToRead(R:x)
|                     serialAvailable()
|                     serialClose()
|                     serialSend(data,ttl)
|                         |
|-------------------------|
"""
 
import serial
import glob
import time


class BuchuSerial():
    baudrate = 9600
    def __init__(self,port):
        print("__init Buchuserial")
        self.portConfig = self.serialBegin(port)

# Setter  for serial baudrete
    def setBaudrate(self, _baudrate):
        self.baudrate = _baudrate

# Can check all available ports and select one 
    def serial_ports(self):
        ports = glob.glob('/dev/ttyUSB*')
        result = []
        for port in ports:
            try:
                s = serial.Serial(port)
                s.close()
                result.append(port)
            except (OSError, serial.SerialException):
#                 pass
                print("Serial Exception " + (OSError ))
        print(result)
        return result

# Begin serial connection
    def serialBegin(self,port):
        try:
            print("Connecting to " + str(port))
            portConfig = serial.Serial(port=port,
                                       baudrate=self.baudrate,
                                       bytesize=serial.EIGHTBITS,
                                       parity=serial.PARITY_NONE,
                                       stopbits=serial.STOPBITS_ONE)
        except:
            ports ='None'
            time.sleep(5)
            self.serialBegin(port)
#             return False
            pass
        return portConfig

# Write a string with serial 
    def serialWriteString(self, xData):
        try:
            self.portConfig.write(str(xData).encode())
            return True
        except serial.SerialException:
            print('Port is not available at write string')
            return False
        except serial.portNotOpenError:
            print('Attempting to use a port that is not open')
            return False
        except:
            #self.portConfig.close()
            print('Write Error: Unknown')
            return False

#Raw serial write
    def serialWrite(self, xData):
        try:
            self.portConfig.write(xData)
            return True
        except serial.SerialException:
            print('Port is not available at write')
            return False
        except serial.portNotOpenError:
            print('Attempting to use a port that is not open')
            return False
        except:
            print('Write Error: Unknown')
            return False

# Open a connection with the specified port 
    def serialOpen(self):
        try:
            self.portConfig.open()
            return True
        except serial.SerialException:
            print('Port is not available in openening')
            return False
        except serial.portNotOpenError:
            print('Attempting to use a port that is not open')
            return False
        except:
            print("Not possible to open port")
            return False

# Read a line from serial
    def serialReadLine(self):
        try:
            return self.portConfig.readline()
        except serial.SerialException:
            print('Port is not available')
            return False
        except serial.portNotOpenError:
            print('Attempting to use a port that is not open in read line')
            return False
        except:
            print("Not possible to read port")
            return False

# Read n bytes from serial port
    def serialxBytesToRead(self, n):
        try:
            return self.portConfig.read(n)
        except serial.SerialException:
            print('Port is not available in read x bytes')
            return False
        except serial.portNotOpenError:
            print('Attempting to use a port that is not open')
            return False
        except:
            print("Not possible to read port")
            return False

# If serial data is available then return true else false
    def serialAvailable(self):
        try:
            if(self.portConfig.in_waiting):
                return True
            else:
                return False
        except serial.SerialException:
            print('Port is not available')
            return False
        except serial.portNotOpenError:
            print('Attempting to use a port that is not open')
            return False

# Try to close if it is already open
    def serialClose(self):
        try:
            self.portConfig.close()
            return True
        except serial.SerialException:
            print('Port is not available in close')
        except serial.portNotOpenError:
            print('Attempting to use a port that is not open')
        except:
            print("Not possible to close port")
            return False

# Try ti send a command and return the answer from this command
    def serialSend(self, xData, TTL=2):
        try:# try to open
            if not self.portConfig.isOpen():
                self.serialOpen()
            # try to send
            self.serialWrite(xData)
            return 1
        except:
            print("Error sending")
            pass
# Serial Flush
    def serialFlush(self):
        try:# try to open
            if not self.portConfig.isOpen():
                self.serialOpen()
            self.portConfig.flush()
            return 1
        except:
            print("Error flush")
            pass
            
   
    def serialSendAndReceive(self, xData, TTL=2):
   # try to open
        try:# try to open
#             if not self.portConfig.isOpen():
#                 self.serialOpen()
            # try to send
            self.serialWrite(xData)
            # try to read if available
            count = 0
            startTimeOut = time.time()
            while (not self.serialAvailable()):
                print("waiting response...")
                endTimeOut = time.time()
                time.sleep(1)
                # TimeOut
                if (endTimeOut - startTimeOut >= TTL):  
                    return -1
            response = self.serialReadLine()
            # print(response)
            return response
        except:
            print("Error sending")
            pass
            

