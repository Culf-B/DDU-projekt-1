import serial

class SerialReader:
    def __init__(self, port = "COM6", baudrate = 9600, timeout = .1):
        self.arduino = serial.Serial(port=port, baudrate=baudrate, timeout=timeout)

    def read(self):
        return self.arduino.readline()

    def formatRead(self):
        return str(self.read())[2:5].split(",")