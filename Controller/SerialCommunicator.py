import serial, time

class SerialCommunicator:
    def __init__(self, port, baudrate=9600, timeout=0.2, parity=serial.PARITY_EVEN):
        print("SerialCommunicator")
        self.port = port
        self.baudrate = baudrate
        self.parity = parity
        self.timeout = timeout
        self.is_open = False
        self.initializeSerial()

    def open_port(self):
        try:
            print("trying to open port " + str(self.port))
            self.com = serial.Serial(self.port, self.baudrate, serial.EIGHTBITS,self.parity, timeout=self.timeout )
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
            msg = self.com.readline()
            print(msg.decode())
            return self.com.readline()
        else:
            print("Not open")
            return ""

    def initializeSerial(self):
        print("initializeSerial")
        self.open_port()
        self.com.reset_input_buffer()
        self.com.reset_output_buffer()