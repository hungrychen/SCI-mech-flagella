import serial
import datetime
import time

SERIAL_ADDRESS = '/dev/cu.usbmodem1101'
BAUD_RATE = 2.5e5
SER_TIMEOUT = 5.
SER_READ_AMT = 10
STARTUP_DELAY = 1.
MOTOR_START_DELAY = 30.
MOTOR_STOP_DELAY = 30.
TIME = datetime.datetime.now()
FILENAME = 'mech_flagella_data_' \
  + str(TIME.year) + '_' + str(TIME.month) + '_' + str(TIME.day) + '_' \
  + str(TIME.hour) + '.' + str(TIME.minute) + '.' + str(TIME.second)

def getRunSettings(num: int):
  output = []
  for i in range(1, num+1):
    print('Enter settings for run %i using the format [speed1] [direction1] [speed2] [direction2]' % i)
    usr_input = input()
    output.append(usr_input.split(' '))
  return output

def getEncodedCommand(command: str):
  return command.encode()

def writeDataToFile(serialReadAmount: int, serialConnection, currentFile):
  encoded_data = serialConnection.read(serialReadAmount)
  currentFile.write(encoded_data.decode())

def startSerial():
    serialConnection = serial.Serial(SERIAL_ADDRESS, BAUD_RATE, timeout=SER_TIMEOUT)
    print('Serial connected. Wait for startup.')
    time.sleep(STARTUP_DELAY)
    return serialConnection

# speeds = []
# while True:
#   print('Enter Speed or enter "q" when finished: ')
#   usr_input = input()
#   if usr_input == 'q':
#     break
#   speeds.append(int(usr_input))
# speeds.sort()

# print('Select motor (1 or 2): ')
# motorSelect = input()
# assert(motorSelect == '1' or motorSelect == '2')

try:
  testSerial = startSerial()
except:
  print('Serial error')
  print('Check serial port')
  exit

testSerial.close()

numRuns = int(input("Enter number of runs: "))
assert(numRuns > 0)
runSettings = getRunSettings(numRuns)

print('Enter data collection duration (in sec): ')
dataCollectTime = int(input())
assert(dataCollectTime > 0)

print('Enter temperature (C): ')
temp = float(input())

currentFile = open(FILENAME+'_SETTINGS.txt', 'x')
for setting in runSettings:
  for item in setting:
    currentFile.write(str(item) + ' ')
  currentFile.write('\n')
currentFile.write('Collection Duration: %i\n' % dataCollectTime)
currentFile.write('Temperature (C): %f\n' % temp)
currentFile.close()

filenames = []
for i in range(1, numRuns+1):
  filenames.append(FILENAME + '_' + str(i) + '.txt')

serialConnection = startSerial()

for i in range(len(filenames)):
  print('Now collecting data for run', i+1)
  currentFile = open(filenames[i], 'x')

  tempTime = int(time.time())
  while (int(time.time()) < tempTime + MOTOR_START_DELAY):
    writeDataToFile(SER_READ_AMT, serialConnection, currentFile)
  
  serialConnection.write( \
    getEncodedCommand('speed 1 = ' + str(runSettings[i][0]) + '\n'))
  time.sleep(.5)
  serialConnection.write( \
    getEncodedCommand('speed 2 = ' + str(runSettings[i][2]) + '\n'))
  print('Motor on')

  tempTime = int(time.time())
  while (int(time.time()) < tempTime + dataCollectTime):
    writeDataToFile(SER_READ_AMT, serialConnection, currentFile)
  
  serialConnection.write(getEncodedCommand('speed 1 = 0' + '\n'))
  time.sleep(.5)
  serialConnection.write(getEncodedCommand('speed 2 = 0' + '\n'))
  print('Motor off')

  tempTime = int(time.time())
  while (int(time.time()) < tempTime + MOTOR_STOP_DELAY):
    writeDataToFile(SER_READ_AMT, serialConnection, currentFile)

  currentFile.close()
  # serialConnection.close()

print('Data collection complete')