import time
import numpy as np
import matplotlib.pyplot as plt
import os

class Config:
    # CONFIG SETTINGS
    VERBOSE = 'verbose'
    USE_PWM = 'usePwm' # default is False: use PI control
    SHORT_DELAY = 'shortDelay'
    DISABLE_ALL_DELAY = 'disableAllDelay'
    DEFAULT_CONFIG = {
        VERBOSE: False,
        USE_PWM: False,
        SHORT_DELAY: False,
        DISABLE_ALL_DELAY: False
    }
    
    # Delays
    tareDelay = 5.
    motorStartDelay = 20.
    motorStopDelay = 100.
    serialStartDelay = 12.
    commandDelay = 0.7

    # Short delays
    SHORT_DELAY_AMT = 5.
    
    def __init__(self, **kwargs):
        if kwargs.keys() != Config.DEFAULT_CONFIG.keys():
            raise ValueError('Wrong keyword arguments')
        self.configDict = kwargs
        if kwargs[Config.SHORT_DELAY]:
            self.motorStartDelay = Config.SHORT_DELAY_AMT
            self.motorStopDelay = Config.SHORT_DELAY_AMT
        if kwargs[Config.DISABLE_ALL_DELAY]:
            self.tareDelay = 0
            self.motorStartDelay = 0
            self.motorStopDelay = 0
            self.serialStartDelay = 0
            self.commandDelay = 0

    def convertSpeedForCommand(self, speed):
        if self.configDict[Config.USE_PWM]:
            return speed
        # return speed/6*21
        # Updated for new low speed motors
        return speed

# This will block until completed
def wait(waitFromTime: float, waitDuration: float, verbose=False):
    readyTime = waitFromTime + waitDuration
    while time.time() < readyTime:
        if verbose:
            print('Waiting, %.1fs remaining' % (readyTime-time.time()))
        time.sleep(0.5)


def previewData(filePath: str, useSameFileName: bool):
    data = np.loadtxt(filePath, delimiter=",")
    t = data[:,0]
    lc1 = data[:,1]
    lc2 = data[:,3]
    previewFileName = 'preview-1'
    previewFileExt = 'png'
    dirname = os.path.dirname(filePath)

    while os.path.isfile(dirname + '/' + '.'.join((previewFileName, previewFileExt))):
        l = previewFileName.split('-')
        l[-1] = str(int(l[-1]) + 1)
        previewFileName = '-'.join(l)
    
    if useSameFileName:
        previewFileName = os.path.basename(filePath).split(".txt")[0]

    plt.clf()
    plt.plot(t, lc1, label='lc1')
    plt.plot(t, lc2, label='lc2')
    plt.legend()
    plt.grid()
    plt.savefig(dirname + '/' + '.'.join((previewFileName, previewFileExt)))
