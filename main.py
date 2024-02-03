import expparams
import files
import connection
import utils
import time

# Check utils for config settings
def main(**kwargs):
    conn = connection.ConnectionManager()
    startTime = time.time()
    params = expparams.Parameters()
    fileMgr = files.FileManager(params, 'expData')

    print('Wait for serial connection')
    utils.wait(startTime, utils.SERIAL_START_DELAY,
               kwargs[utils.VERBOSE])
    
    print('Ready, starting data collection')
    for idx in range(params.getNumTrials()):
        execTrial(conn, params, fileMgr, **kwargs)
    print('Data collection complete')

def execTrial(conn: connection.ConnectionManager,
              params: expparams.Parameters, fileMgr: files.FileManager,
              **kwargs):
    pass

    # Open the file for writing

    # Tare the load cell

    # Send speed command

    # Record data

    # Turn off motors

if __name__ == '__main__':
    main(**utils.DEFAULT_CONFIG)
