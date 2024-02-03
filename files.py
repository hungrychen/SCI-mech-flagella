import expparams
import datetime
import time
import sys
import serial
import re

class FileManager:
    TRIAL_NUM_TAG = '_t_'
    DEBUG_FILE_TAG = '_DEBUG-LOG_'
    DEF_FILE_EXT = '.txt'
    REGEX_VLD_DATA = r'^(-*\d+\.\d+,){9}(\d+,\d+)$'

    def __init__(self, parameters: expparams.Parameters,
                 fileHeader: str, fileExtension: str = DEF_FILE_EXT):
        self.parameters = parameters
        self.fileHeader = fileHeader
        self.fileExtension = fileExtension
        self.currentFile = None
        self.debugFile = None

        timeStamp = str(datetime.datetime.now())
        timeStamp = timeStamp[:timeStamp.index('.') + 2]
        timeStamp = ''.join(c if c.isalnum() else '-' for c in timeStamp)
        debugFileName = (fileHeader + FileManager.DEBUG_FILE_TAG +
                         timeStamp + fileExtension)
        try:
            self.debugFile = open(debugFileName, 'x')
        except:
            sys.stderr.write(
                'Debug file creation error: Wait a few secs, then try again')
            exit(1)
    
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
                            self.parameters.getFileString(trialIndex) +
                            FileManager.TRIAL_NUM_TAG + str(fileNum) +
                            self.fileExtension)
                self.currentFile = open(fileName, 'x')
            except FileExistsError:
                fileNum += 1
            else:
                fileOpenSuccess = True
                print('Opened the file for writing: ' + fileName)

    def recordData(self, serialConnection: serial.Serial):
        regexComp = re.compile(FileManager.REGEX_VLD_DATA)
        inputText = serialConnection.readline().decode(errors='backslashreplace')
        if re.match(regexComp, inputText):
            self.currentFile.write(inputText)
            return True
        self.debugFile.write(inputText)
        return False
    
    def recordDataForDuration(self, serialConnection: serial.Serial, duration: float):
        start = time.time()
        while time.time() < start + float(duration):
            self.recordData(serialConnection)

if __name__ == '__main__':
    # testParams = expparams.Parameters()
    # testFileManager = FileManager(testParams, 'FILE-HEADER', '.EXT')
    # print('Instantiated a FileManager object: ' + str(testFileManager))
    # print()
    # print('__dict__: ' + str(testFileManager.__dict__))
    # testFileManager.openFile(0)
    # testFileManager.openFile(1)

    import unittest
    from unittest.mock import Mock

    class TestFileManager(unittest.TestCase):
        def setUp(self):
            self.testParams = expparams.Parameters()
            self.testFileManager = FileManager(self.testParams, 'FILE-HEADER', '.EXT')
            self.testFileManager.openFile(0)

        def test_recordData(self):
            serialConnection = Mock(spec=serial.Serial)
            serialConnection.readline.return_value =\
                b'-0.81255,-0.80950,0.63760,0.62898,54.3650,53.63,54.79,26.81,42.42,0,0\n'
            self.assertTrue(self.testFileManager.recordData(serialConnection))

        def test_recordData_invalid(self):
            serialConnection = Mock(spec=serial.Serial)
            serialConnection.readline.return_value = b'invalid data\n'
            self.assertFalse(self.testFileManager.recordData(serialConnection))

        # def test_recordDataForDuration(self):
        #     serialConnection = Mock(spec=serial.Serial)
        #     serialConnection.readline.return_value = b'valid data\n'
        #     self.testFileManager.recordDataForDuration(serialConnection, 0.1)

    unittest.main()
