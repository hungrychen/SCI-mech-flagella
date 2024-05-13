import expparams
import datetime
import time
import sys
import serial
import re
import os

class FileManager:
    TRIAL_NUM_TAG = '_t_'
    DEBUG_FILE_TAG = '_DEBUG-LOG_'
    DEF_FILE_EXT = '.txt'
    REGEX_VLD_DATA = r'(-?\d+\.\d+,){9}(\d+,){3}(\d+)'

    def __init__(self, parameters: expparams.Parameters,
                 fileHeader: str, writePath: str = '.', fileExtension: str = DEF_FILE_EXT):
        self.parameters = parameters
        self.fileHeader = fileHeader
        self.fileExtension = fileExtension
        self.currentFile = None
        self.debugFile = None
        self.writePath = writePath + '/'
        self.regexComp = re.compile(FileManager.REGEX_VLD_DATA)

        timeStamp = str(datetime.datetime.now())
        timeStamp = timeStamp[:timeStamp.index('.') + 2]
        timeStamp = ''.join(c if c.isalnum() else '-' for c in timeStamp)
        debugFileName = (fileHeader + FileManager.DEBUG_FILE_TAG +
                         timeStamp + fileExtension)
        try:
            self.debugFile = open(self.writePath + debugFileName, 'x')
        except:
            sys.stderr.write(
                'Debug file creation error: Wait a few secs, then try again\n')
            exit(1)
        else:
            print('ALERT: The current directory is: ' + os.getcwd())
            print('Opened the debug file for writing: ' + debugFileName)

    def __del__(self):
        if self.currentFile is not None:
            self.currentFile.close()
        if self.debugFile is not None:
            self.debugFile.close()

    def openFile(self, trialIndex):
        if self.currentFile is not None:
            self.currentFile.close()
        fileNum = 1
        fileName = str()
        fileOpenSuccess = False
        while not fileOpenSuccess:
            try:
                fileName = (self.fileHeader + 
                    self.parameters.getFileString(trialIndex, onlySelectedParam=True) +
                    FileManager.TRIAL_NUM_TAG + str(fileNum) +
                    self.fileExtension)
                self.currentFile = open(self.writePath + fileName, 'x')
            except FileExistsError:
                fileNum += 1
            else:
                fileOpenSuccess = True
                self.currentFilePath = self.writePath + fileName
                print('Opened the file for writing: ' + fileName)

    def writeParams(self):
        self.debugFile.write('\n***Params for Experiment***\n')

        for item in [self.parameters.paramDict]:
            writeList = [s for s in str(item).split(',')]
            [self.debugFile.write(s+'\n') for s in writeList]
            self.debugFile.write('\n')
        self.debugFile.write(str(self.parameters.omegaList))

        self.debugFile.write('\n***************************\n')
        print('Wrote params to debug file')

    def recordData(self, serialConnection: serial.Serial,
                   isExpData: bool = True):
        inputText = serialConnection.readline().decode(errors='backslashreplace')
        if isExpData and re.match(self.regexComp, inputText):
            self.currentFile.write(inputText)
            return True
        self.debugFile.write(inputText)
        return False

    # This will block until data recording is complete
    def recordDataForDuration(self, serialConnection: serial.Serial, duration: float,
                              isExpData: bool = True):
        print('Recording %s data for %.1fs' %
              (('exp' if isExpData else 'non-exp'), duration))
        start = time.time()
        while time.time() < start + float(duration):
            self.recordData(serialConnection, isExpData)
        print('Data recording complete')

    def getCurrentFilePath(self) -> str:
        return self.currentFilePath

if __name__ == '__main__':
    pass
