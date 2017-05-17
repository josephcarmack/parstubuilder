

class ParametricStudy:

    def __init__(self,**kwargs):
        if len(kwargs) == 0:
            self.studyName = 'Study Name'
            self.pathToStudy = 'path-to-study'
            self.inputFileGen = 'input file generator executable name'
            self.inputFileMod = 'input file modifier executable name'
            self.parametric_info = {}
        else:
            self.studyName = 'Study Name'
            self.pathToStudy = 'path-to-study'
            self.inputFileGen = 'input file generator executable name'
            self.inputFileMod = 'input file modifier executable name'
            self.parametric_info = {}
            validKwargs = {
                    'studyName':self.studyName,
                    'pathToStudy':self.pathToStudy,
                    'inputFileGen':self.inputFileGen,
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
            self.inputFileGen = validKwargs['inputFileGen']
            self.inputFileMod = validKwargs['inputFileMod']
            self.parametric_info = validKwargs['parametric_info']
