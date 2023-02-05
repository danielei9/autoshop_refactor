import serial, time

class SerialCommunicator:
    def __init__(self, port, baudrate=9600, timeout=0.2):
        print("SerialCommunicator")
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.is_open = False
        self.initializeSerial()

    def open_port(self):
        try:
            print("trying to open port " + str(self.port))
            self.com = serial.Serial(self.port, self.baudrate, serial.EIGHTBITS, serial.PARITY_EVEN, timeout=self.timeout )
            if(self.com.is_open):
                self.close_port()
                time.sleep(.2)
            else:
                self.com.open()
        except serial.SerialException as e:
            print("ERROR: error opening port " + (self.port))
            raise e
        
    def close_port(self):
        if self.is_open:
            self.com.close()
            self.is_open = False

    def send_data(self, data):
        if self.is_open:
            self.com.write(data).encode()
    
    def receive_data(self):
        if self.is_open:
            return self.com.readline()
        else:
            print("Not open")
            return ""

    def initializeSerial(self):
        print("initializeSerial")
        self.open_port()
        self.com.flushInput()
        self.com.flushOutput()