import expparams
import serial
import sys
import time

class ConnectionManager:
    SERIAL_ADDRESS = 'COM8'
    BAUD_RATE = 2.5e5
    TIMEOUT = 5.

    def __init__(self, baud=BAUD_RATE, address=SERIAL_ADDRESS):
        self.baud = baud
        self.address = address
        try:
            self.connection = serial.Serial(port=address,
                baudrate=baud, timeout=ConnectionManager.TIMEOUT)
        except:
            sys.stderr.write('***\nSerial connection error, check serial connection\n***\n')
            time.sleep(3.)
            raise ConnectionError()
        else:
            print('Connected to serial at %s' % self.address)

    def __del__(self):
        self.setSpeedZero()
        self.connection.close()
        print('Serial connection closed at %s' % self.address)

    def setSpeedZero(self):
        self.updateSpeedManual([0 for _ in range(2)])

    def getConnection(self):
        return self.connection
    
    def sendCommand(self, command: str):
        self.connection.write((command+'\n\n').encode())
        print('Wrote the cmd to serial: ' + command)

    def updateSpeedByTrial(self, trialIndex: int, parameters: expparams.Parameters,
                           conversionFunction = None):
        IDX_EXTRACT = (expparams.Parameters.OMEGA_1_IDX, expparams.Parameters.OMEGA_2_IDX)
        speedList = parameters.getOmegas(trialIndex)
        speeds = [speedList[idx] for idx in IDX_EXTRACT]
        self.updateSpeedManual(speeds, conversionFunction)

    def updateSpeedManual(self, speeds, conversionFunction = None):
        finalSpeeds = []
        if conversionFunction is not None:
            finalSpeeds = [conversionFunction(speed) for speed in speeds]
        else:
            finalSpeeds = speeds
        finalSpeeds = [int(speed) for speed in finalSpeeds]
        SPEED_CMD = 'speed'
        SPEED_CMD_SET = '='
        for idx in range(len(finalSpeeds)):
            cmd = SPEED_CMD +\
                ' ' + str(idx+1) + ' ' + SPEED_CMD_SET +\
                ' ' + str(finalSpeeds[idx])
            self.sendCommand(cmd)
    
    def sendTare(self):
        TARE_CMD = 'tare'
        self.sendCommand(TARE_CMD)

if __name__ == '__main__':
    pass
