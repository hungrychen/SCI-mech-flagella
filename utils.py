import time

class Config:
    # CONFIG SETTINGS
    VERBOSE = 'verbose'
    USE_PWM = 'usePwm' # default is False: use PI control
    SHORT_DELAY = 'shortDelay'
    DEFAULT_CONFIG = {
        VERBOSE: False,
        USE_PWM: False,
        SHORT_DELAY: False
    }
    
    # Delays
    tareDelay = 5.
    serialStartDelay = 12.
    motorStartDelay = 20.
    motorStopDelay = 100.

    # Short delays
    SHORT_DELAY_AMT = 5.
    
    def __init__(self, **kwargs):
        if kwargs.keys() != Config.DEFAULT_CONFIG.keys():
            raise ValueError('Wrong keyword arguments')
        self.configDict = kwargs
        if kwargs[Config.SHORT_DELAY]:
            self.motorStartDelay = Config.SHORT_DELAY_AMT
            self.motorStopDelay = Config.SHORT_DELAY_AMT

    def convertSpeedForCommand(self, speed):
        if self.configDict[Config.USE_PWM]:
            return speed
        return speed/6*21

# This will block until completed
def wait(waitFromTime: float, waitDuration: float, verbose=False):
    readyTime = waitFromTime + waitDuration
    while time.time() < readyTime:
        if verbose:
            print('Waiting, %.1fs remaining' % (readyTime-time.time()))
        time.sleep(0.5)
