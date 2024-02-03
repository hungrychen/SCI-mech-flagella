import expparams
import serial
import sys

class ConnectionManager:
    SERIAL_ADDRESS = 'COM8'
    BAUD_RATE = 2.5e5
    TIMEOUT = 5.

    def __init__(self, baud=BAUD_RATE, address=SERIAL_ADDRESS):
        self.baud = baud
        self.address = address
        try:
            self.connection = serial.Serial(address=address,
                baudrate=baud, timeout=ConnectionManager.TIMEOUT)
        except:
            sys.stderr.write('Serial connection error, check serial connection\n')
        else:
            print('Connected to serial at %s' % self.address)

    def __del__(self):
        self.connection.close()

    def getConnection(self):
        return self.connection

    def updateSpeedByTrial(self, parameters: expparams.Parameters, trialIndex: int):
        speedList = parameters.omegaList[trialIndex]
        pass

    def updateSpeedManual(self, speeds):
        pass

if __name__ == '__main__':
    pass