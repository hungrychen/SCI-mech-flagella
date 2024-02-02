class expparams:
    masterParams = [
        # ('temp', float),
        ('numRod', int), ('helixPitch', float),
        ('helixRadius', float), ('rodRadius', float),
        ('youngM', float), ('Poisson', float),
        ('viscosity', float), ('axisLenghInput', float),
        ('distance', float), ('density', float)
        # ('omega1', float), ('omega2', float),
        # ('totalTime', float)
    ]

    def __init__(self):
        self.userParams = []
        self.fileString = str()
        for key, item in self.masterParams:
            self.userParams.append(item(input('Enter %s: ' % key)))

    def updateFileString(self):
        self.fileString = str()
        for idx in range(len(self.userParams)):
            self.fileString += (
                '_' + self.masterParams[idx][0] +
                '_' + str(self.userParams[idx])
            )

    def getFileString(self):
        self.updateFileString()
        return self.fileString

if __name__ == '__main__':
    test = expparams()
    print()
    print('You have instantiated an object: ' + str(test))
    print(test.__dict__)
    print('getFileString(): ' + test.getFileString())
