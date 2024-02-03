class Parameters:
    NUM_ROD = 'numRod';           HELIX_PITCH = 'helixPitch'
    HELIX_RADIUS = 'helixRadius'; ROD_RADIUS = 'rodRadius'
    YOUNG_M = 'youngM';           POISSON = 'Poisson'
    VISCOSITY = 'viscosity';      AXIS_LENGTH_INPUT = 'axisLengthInput'
    DISTANCE = 'distance';        DENSITY = 'density'
    OMEGA1 = 'omega1';            OMEGA2 = 'omega2'
    TOTAL_TIME = 'totalTime'  # Time per trial [s]
    NUM_TRIALS = 'numTrials'

    PARAM_TYPES = dict([
        (NUM_ROD, int), (HELIX_PITCH, float),
        (HELIX_RADIUS, float), (ROD_RADIUS, float),
        (YOUNG_M, float), (POISSON, float),
        (VISCOSITY, float), (AXIS_LENGTH_INPUT, float),
        (DISTANCE, float), (DENSITY, float),
        (OMEGA1, float), (OMEGA2, float),
        (TOTAL_TIME, int), (NUM_TRIALS, int)
    ])
    PARAM_FILE_STRING = (
        NUM_ROD, HELIX_PITCH, HELIX_RADIUS, ROD_RADIUS,
        YOUNG_M, POISSON, VISCOSITY, AXIS_LENGTH_INPUT,
        DISTANCE, DENSITY, OMEGA1, OMEGA2, TOTAL_TIME
    )
    PARAM_ENTRY = (
        NUM_ROD, HELIX_PITCH, HELIX_RADIUS, ROD_RADIUS,
        YOUNG_M, POISSON, VISCOSITY, AXIS_LENGTH_INPUT,
        DISTANCE, DENSITY, NUM_TRIALS, TOTAL_TIME
    )

    def __init__(self):
        self.paramDict = {}
        self.omegaList = []
        self.fileString = str()
        
        for param in Parameters.PARAM_ENTRY:
            self.paramDict[param] = Parameters.PARAM_TYPES[param](input('Enter %s: ' % param))
        
        if self.paramDict[Parameters.TOTAL_TIME] < 0:
            raise ValueError('You must enter a positive trial duration')
        if self.paramDict[Parameters.NUM_TRIALS] < 0:
            raise ValueError('You must enter a positive number of trials')
        
        self.collectOmegas(self.paramDict[Parameters.NUM_TRIALS])
    
    def getFileString(self, trialIndex=None):
        if trialIndex is not None:
            self.updateOmegas(trialIndex)
        self.updateFileString()
        return self.fileString

    def collectOmegas(self, trials):
        RESERVED_COLS = (1, 3)
        self.omegaList = []
        for idx in range(trials):
            inputList = input(('Enter settings for run %i' % (idx+1)) +
                        ' using the format [speed1] [-0-] [speed2] [-0-]: ')\
                        .split(' ')
            inputList = [int(num) for num in inputList]
            try:
                for col in RESERVED_COLS:
                    if inputList[col] != 0: print('WARNING: reserved cols (1, 3) not in use')
            except IndexError:
                raise ValueError('You must enter 4 values separated by a space')
            self.omegaList.append(inputList)

    def updateFileString(self):
        self.fileString = str()
        for param in Parameters.PARAM_FILE_STRING:
            self.fileString += (
                '_' + param +
                '_' + str(self.paramDict.get(param, 'NONE'))
            )

    def updateOmegas(self, trialIndex):
        OMEGA_1_IDX = 0; OMEGA_2_IDX = 2
        trialOmegaList = self.omegaList[trialIndex]
        self.paramDict[Parameters.OMEGA1] = trialOmegaList[OMEGA_1_IDX]
        self.paramDict[Parameters.OMEGA2] = trialOmegaList[OMEGA_2_IDX]

if __name__ == '__main__':
    test = Parameters()
    print()
    print('You have instantiated an object: ' + str(test))
    print()
    print('__dict__: ' + str(test.__dict__))
    print()
    print(test.getFileString())
    print()
    print('test getFileString(): ' + test.getFileString(1))
    print()
    print('test getFileString(): ' + test.getFileString(2))
    print()
    test.updateOmegas(0)
    print('test getFileString(): ' + test.getFileString())
    print()
