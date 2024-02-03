import time

# CONFIG SETTINGS
VERBOSE = 'verbose'
USE_PWM = 'pwm'
DEFAULT_CONFIG = {
    VERBOSE: False,
    USE_PWM: False
    }

# DELAYS
TARE_DELAY = 5.
SERIAL_START_DELAY = 12.

# This will block until completed
def wait(waitFromTime: float, waitDuration: float, verbose=False):
    readyTime = waitFromTime + waitDuration
    while time.time() < readyTime:
        if verbose:
            print('Waiting, %.1fs remaining' % (readyTime-time.time()))
        time.sleep(0.5)
