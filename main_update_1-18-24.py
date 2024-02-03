import serial
import datetime
import time
import re

from expparams import *

SERIAL_ADDRESS = 'COM8'
BAUD_RATE = 2.5e5
SER_TIMEOUT = 5.
SER_READ_AMT = 10
STARTUP_DELAY = 1.
INIT_DELAY = 12.
TARE_TIME = 6.5
MOTOR_START_DELAY = 20.
MOTOR_STOP_DELAY = 100.
INTERMEDIATE_TARE: bool = True
TIME = datetime.datetime.now()
FILENAME = 'expData'
TIMESTAMP = str(TIME.year) + '_' + str(TIME.month) + '_' + str(TIME.day) + '_' \
  + str(TIME.hour) + '.' + str(TIME.minute) + '.' + str(TIME.second)

CONTROL_ENABLE = 1
MODE_HIGH_INITIAL = 0
DEBUG = 1

if DEBUG:
  MOTOR_START_DELAY = 5.
  MOTOR_STOP_DELAY = 5.
  print('\n*****\nDEBUG ENABLED\n*****\n')

def getRunSettings(num: int):
  output = []
  for i in range(1, num+1):
    print('Enter settings for run %i using the format [speed1] [direction1] [speed2] [direction2]' % i)
    usr_input = input()
    output.append(usr_input.split(' '))
  return output

# Must end with newline to send command properly
def getEncodedCommand(command: str):
  return command.encode()

def writeDataToFile(serialReadAmount: int, serialConnection, currentFile):
  # encoded_data = serialConnection.read(serialReadAmount)
  encoded_data = serialConnection.readline()
  text = encoded_data.decode(errors='backslashreplace')
  match = re.compile('(-*\d+.\d+,){9}01')
  if re.match(match, text):
    currentFile.write(text)
  else:
    settingsFile.write(text)

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
  if DEBUG:
    print('***DEBUG active. Proceeding without Serial connection***')
  else:
    print('Serial error')
    print('Check serial port')
    exit(1)
else:
  testSerial.close()

numRuns = int(input("Enter number of runs: "))
assert(numRuns > 0)
runSettings = getRunSettings(numRuns)

print('Enter data collection duration (in sec): ')
dataCollectTime = int(input())
assert(dataCollectTime > 0)

# print('Enter temperature (C): ')
# temp = float(input())

# print('Enter helix pitch')
# helixPitch = float(input())

# print('Enter helix radius')
# helixRadius = float(input())

# print('Enter rod radius')
# rodRadius = float(input())

# print('Enter axis length input')
# axisLengthInput = float(input())

myExpParams = Parameters()

settingsFile = open(FILENAME+TIMESTAMP+'_SETTINGS.txt', 'x')
for setting in runSettings:
  for item in setting:
    settingsFile.write(str(item) + ' ')
  settingsFile.write('\n')
settingsFile.write('Collection Duration: %i\n' % dataCollectTime)
# settingsFile.write('Temperature (C): %f\n' % temp)

# settingsString = '_helixPitch_' + str(helixPitch) + '_helixRadius_' + str(helixRadius) + '_rodRadius_' \
#   + str(rodRadius) + '_axisLengthInput_' + str(axisLengthInput)
settingsString = myExpParams.getFileString()
filenames = []
for i in range(len(runSettings)):
  val0 = int(runSettings[i][0])
  val1 = int(runSettings[i][2])
  # use0 = abs(val0) > abs(val1)
  # omega = val0 if use0 else val1
  filenames.append(FILENAME + settingsString + '_omega1_' + str(val0) + '_omega2_' + str(val1) \
                  + '_totalTime_' + str(dataCollectTime)) # add index and .txt later

# prevOmega = int()
# prevTrialIndex = int()
# for i in range(len(runSettings)):
#   omega = max(runSettings[i][0], runSettings[i][2])
#   trialIndex = int(1)
#   if omega == prevOmega:
#     trialIndex = prevTrialIndex+1
#   filenames.append(FILENAME + settingsString + '_omega_' + str(omega) \
#                    + '_totalTime_' + str(dataCollectTime) + '_t_' + str(trialIndex) + '.txt')
#   prevOmega = omega
#   prevTrialIndex = trialIndex

serialConnection = startSerial()
print('Wait for start:')
tempTime = int(time.time())
while (int(time.time()) < tempTime + INIT_DELAY):
  writeDataToFile(SER_READ_AMT, serialConnection, settingsFile)

for i in range(len(filenames)):
  print('Now collecting data for run', i+1)

  fileOpenStatus = False
  fileIndex = int(1)
  while not fileOpenStatus:
    try:
      currentFile = open(filenames[i] + '_t_' + str(fileIndex) + '.txt', 'x')
      fileOpenStatus = True
    except FileExistsError:
      fileIndex += 1
      if fileIndex == 99999:
        print('File Error')
        while 1:
          pass

  if INTERMEDIATE_TARE:
    serialConnection.write(getEncodedCommand('tare'))
    print('TARE')

  tempTime = int(time.time())
  while (int(time.time()) < tempTime + TARE_TIME):
    writeDataToFile(SER_READ_AMT, serialConnection, settingsFile)
  serialConnection.flush()

  tempTime = int(time.time())
  while (int(time.time()) < tempTime + MOTOR_START_DELAY):
    writeDataToFile(SER_READ_AMT, serialConnection, currentFile)

  cmdA_val = int(runSettings[i][0])
  cmdB_val = int(runSettings[i][2])

  if MODE_HIGH_INITIAL:
    print('Run high initial')
    if cmdA_val > 0:
      serialConnection.write(getEncodedCommand('speed 1 = 40\n'))
      time.sleep(.1)
    elif cmdA_val < 0:
      serialConnection.write(getEncodedCommand('speed 1 = -40\n'))
      time.sleep(.1)
    if cmdB_val > 0:
      serialConnection.write(getEncodedCommand('speed 2 = 38\n'))
      time.sleep(.1)
    elif cmdB_val < 0:
      serialConnection.write(getEncodedCommand('speed 2 = -38\n'))
      time.sleep(.1)
    time.sleep(1)
    print('End high initial')
  
  if CONTROL_ENABLE:
    cmdA_val = cmdA_val/6*21
    cmdB_val = cmdB_val/6*21

  serialConnection.write( \
    getEncodedCommand('\nspeed 1 = ' + str(cmdA_val) + '\n\n'))
  print('wrote: ' + 'speed 1 = ' + str(cmdA_val) + '\n')
  time.sleep(.1)
  serialConnection.write( \
    getEncodedCommand('\nspeed 2 = ' + str(cmdB_val) + '\n\n'))
  print('wrote: ' + 'speed 2 = ' + str(cmdB_val) + '\n')
  time.sleep(.1)
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
serialConnection.write(getEncodedCommand('tare'))
settingsFile.close()
