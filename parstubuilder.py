import os

class ParametricStudy:

    def __init__(self,**kwargs):
        if len(kwargs) == 0:
            self.studyName = 'Study Name'
            self.pathToStudy = 'path-to-study'
            self.defaultInputFileName = 'defaultInputFile.dat'
            self.inputFileMod = 'input file modifier executable name'
            self.parametric_info = {}
        else:
            self.studyName = 'Study Name'
            self.pathToStudy = 'path-to-study'
            self.defaultInputFileName = 'defaultInputFile.dat'
            self.inputFileMod = 'input file modifier executable name'
            self.parametric_info = {}
            validKwargs = {
                    'studyName':self.studyName,
                    'pathToStudy':self.pathToStudy,
                    'defaultInputFileName':self.defaultInputFileName,
                    'inputFileMod':self.inputFileMod,
                    'parametric_info':self.parametric_info
                    }

            # check for valid keyword arguments
            for key in kwargs:
                if key not in validKwargs:
                    eflag = key
                    print(str(eflag)+' is not a valid keyword! Valid keyword args:')
                    for k in validKwargs:
                        print(k)
                    raise ValueError('invalid keyword argument')

            # assign keyword args to respective class attributes
            for key in kwargs:
                validKwargs[key] = kwargs[key]
            self.studyName = validKwargs['studyName']
            self.pathToStudy = validKwargs['pathToStudy']
            self.defaultInputFileName = validKwargs['defaultInputFileName']
            self.inputFileMod = validKwargs['inputFileMod']
            self.parametric_info = validKwargs['parametric_info']


    def build(self):

        # -----------------------------
        # create main study directory
        # -----------------------------

        try:
            os.makedirs(self.pathToStudy + self.studyName)
        except OSError:
            print('study directory '+self.pathToStudy+self.studyName+
                    ' already exists. Creating variant study directory.')
            os.makedirs(self.pathToStudy + self.studyName+'1')

        # ------------------------------------------------
        # create subdirectories for parametric study (i.e. 
        # one for each unique set of parameters)
        # ------------------------------------------------

        # calculate the total number of unique parameter sets
        numberOfParamSets = 1
        for k in sorted(self.parametric_info):
            numberOfParamSets *= len(self.parametric_info[k])
        
        # make a list that holds a dictionary for each unique parameter set
        container = self.parametric_info.copy()
        for k in container:
            container[k] = 0
        listOfSets = []
        for i in range(numberOfParamSets):
            listOfSets.append(container.copy())

        # calculate each unique parameter set
        skip = 1
        for parameter in sorted(self.parametric_info):
            numParValues = len(self.parametric_info[parameter])
            val_i =0
            for i in range(numberOfParamSets):
                listOfSets[i][parameter] = self.parametric_info[parameter][val_i]
                if i%skip == 0:
                    val_i += 1
                if val_i == numParValues:
                    val_i = 0
            skip *= numParValues

        # loop over list of unique param sets and create directories
        for s in listOfSets:
            subDirName = '/'
            for param in s:
                subDirName += str(param)+str(s[param])
            os.makedirs(self.pathToStudy+self.studyName+subDirName)
