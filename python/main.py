import expparams
import files
import connection
import utils
import time
import sys
import os

# Check utils for config settings
def main(**kwargs):
    config = utils.Config(**kwargs)
    conn = connection.ConnectionManager()
    startTime = time.time()
    params = expparams.Parameters()
    writePath = sys.argv[1]
    # print('WRITEPATH:', writePath)
    assert os.path.isdir(writePath)
    fileMgr = files.FileManager(params, 'expData', writePath)
    print('Set the write path to:', writePath)

    fileMgr.writeParams()
    print('Wait for serial connection')
    utils.wait(startTime, config.serialStartDelay,
               config.configDict[config.VERBOSE])
    
    print('Ready, starting data collection')
    for idx in range(params.getNumTrials()):
        execTrial(idx, config, conn, params, fileMgr)
    print('Data collection complete')

def execTrial(trialIndex: int,
              config: utils.Config, conn: connection.ConnectionManager,
              params: expparams.Parameters, fileMgr: files.FileManager):
    print('*****************')
    print('Executing trial %i' % (trialIndex+1))

    # Open the file for writing
    fileMgr.openFile(trialIndex)

    # Tare the load cell
    conn.sendTare()
    fileMgr.recordDataForDuration(conn.getConnection(),
                                  config.tareDelay, False)
    
    # Record data prior to motor start
    fileMgr.recordDataForDuration(conn.getConnection(),
                                  config.motorStartDelay)

    # Send speed command
    conn.updateSpeedByTrial(trialIndex,
                            params, config.convertSpeedForCommand)

    # Record data
    fileMgr.recordDataForDuration(conn.getConnection(),
                                  params.getTrialDuration())

    # Turn off motors and record data
    conn.setSpeedZero()
    fileMgr.recordDataForDuration(conn.getConnection(),
                                  config.motorStopDelay)
    
    # Preview the data
    utils.previewData(fileMgr.getCurrentFilePath())
    
    print('Completed trial %i' % (trialIndex+1))
    print('*****************')

if __name__ == '__main__':
    main(**utils.Config.DEFAULT_CONFIG)
    # To run with a different configuration,
    # call main() and pass arguments for all
    # config settings listed in utils.Config
    # Eg.
    # main(verbose=False, usePwm=True, shortDelay=True, disableAllDelay=False)
