import os
import shutil

class ParametricStudy:

    def __init__(self,**kwargs):
        if len(kwargs) == 0:
            self.studyName = None
            self.pathToStudy = None
            self.defaultInputFileName = None
            self.defaultPBSFileName = None
            self.lineMod = None
            self.simExecute = None
            self.parametric_info = None
        else:
            self.studyName = None
            self.pathToStudy = None
            self.defaultInputFileName = None
            self.defaultPBSFileName = None
            self.lineMod = None
            self.simExecute = None
            self.parametric_info = None
            validKwargs = {
                    'studyName':self.studyName,
                    'pathToStudy':self.pathToStudy,
                    'defaultInputFileName':self.defaultInputFileName,
                    'defaultPBSFileName':self.defaultPBSFileName,
                    'lineMod':self.lineMod,
                    'simExecute':self.simExecute,
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
            self.defaultPBSFileName = validKwargs['defaultPBSFileName']
            self.lineMod = validKwargs['lineMod']
            self.simExecute = validKwargs['simExecute']
            self.parametric_info = validKwargs['parametric_info']


    def build(self):


        # ------------------------------------------
        # check to make sure class members have been
        # initialized properly
        # ------------------------------------------

        classMembers = {
                'studyName':self.studyName,
                'pathToStudy':self.pathToStudy,
                'defaultInputFileName':self.defaultInputFileName,
                'defaultPBSFileName':self.defaultPBSFileName,
                'lineMod':self.lineMod,
                'simExecute':self.simExecute,
                'parametric_info':self.parametric_info
                }
        goodInitialization = True
        for mem in classMembers:
            if classMembers[mem] == None:
                goodInitialization = False
                print('Class member '+mem+' was not initialized to an')
                print('appropriate value or data structure.')
        if not goodInitialization:
            print('You must initialize all class members before attempting')
            print('to build a parametric study. Class members that must be')
            print('initialized include:')
            for mem in classMembers:
                print(mem)
        assert goodInitialization

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
        # create subdirectories, input files, executables,
        # and PBS files for the parametric study (i.e. 
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

        # loop over list of unique param sets and create directories and files
        for s in listOfSets:

            # create sub directories
            subDirName = '/'
            for param in s:
                subDirName += str(param)+str(s[param])
            pathPlusSub = self.pathToStudy+self.studyName+subDirName 
            os.makedirs(pathPlusSub)

            # populate sub-directory with input file, sim exec, and PBS file
            os.system('cp ' + self.defaultInputFileName + ' ' + pathPlusSub)
            os.system('cp ' + self.defaultPBSFileName + ' ' + pathPlusSub)
            os.system('cp ' + self.simExecute + ' ' + pathPlusSub)

            # modify input file by looping over each parameter to be modified
            for par in s:
                # input file in current sub-directory
                curInFi = pathPlusSub+'/'+self.defaultInputFileName
                # create temporary copy of input file
                tempInFi = pathPlusSub+'/temp'
                shutil.copy(curInFi,tempInFi)
                # read from temp and write modified version to original
                with open(tempInFi,'r') as fin:
                    with open(curInFi,'w') as fout:
                        for line in fin:
                            if par in line:
                                modifiedLine = self.lineMod(line,par,s[par])
                                fout.write(modifiedLine)
                            else:
                                fout.write(line)
                    fout.close()
                    fin.close()
                    os.remove(tempInFi)
