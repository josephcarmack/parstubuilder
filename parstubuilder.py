import os
import shutil
import subprocess as sp

class ParametricStudy:

    def __init__(self,**kwargs):
        self.startDir = os.getcwd()
        self.numOfParamSets = None
        self.subDir = None
        self.listOfSets = None
        self.buildComplete = False
        self.allJobs = None
        if len(kwargs) == 0:
            self.studyName = None
            self.pathToStudy = None
            self.defaultInputFileName = None
            self.defaultPBSFileName = None
            self.lineMod = None
            self.parametric_info = None
        else:
            self.studyName = None
            self.pathToStudy = None
            self.defaultInputFileName = None
            self.defaultPBSFileName = None
            self.lineMod = None
            self.parametric_info = None
            validKwargs = {
                    'studyName':self.studyName,
                    'pathToStudy':self.pathToStudy,
                    'defaultInputFileName':self.defaultInputFileName,
                    'defaultPBSFileName':self.defaultPBSFileName,
                    'lineMod':self.lineMod,
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
            self.parametric_info = validKwargs['parametric_info']

    # special method used to sort list of dictionaries
    def specialSort(self,dic):
        crit = []
        mykeys = sorted(dic.keys())
        for key in mykeys:
            crit.append(dic[key])
        return tuple(crit)

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
        self.numOfParamSets = 1
        for k in sorted(self.parametric_info):
            self.numOfParamSets *= len(self.parametric_info[k])

        # make a list that holds a dictionary for each unique parameter set
        container = self.parametric_info.copy()
        for k in container:
            container[k] = 0
        self.listOfSets = []
        for i in range(self.numOfParamSets):
            self.listOfSets.append(container.copy())

        # calculate each unique parameter set
        skip = 1
        for parameter in sorted(self.parametric_info):
            numParValues = len(self.parametric_info[parameter])
            val_i =0
            for i in range(self.numOfParamSets):
                self.listOfSets[i][parameter] = self.parametric_info[parameter][val_i]
                if i%skip == 0:
                    val_i += 1
                if val_i == numParValues:
                    val_i = 0
            skip *= numParValues

        # sort parameter sets list
        self.listOfSets.sort(key=self.specialSort)

        # loop over list of unique param sets and create directories and files
        self.subDir = []
        for s in self.listOfSets:

            # create sub directories
            subDirName = '/'
            for param in s:
                subDirName += str(param)+str(s[param])
            pathPlusSub = self.pathToStudy+self.studyName+subDirName
            self.subDir.append(pathPlusSub)

            os.makedirs(pathPlusSub)

            # populate sub-directory with input file, sim exec, and PBS file
            os.system('cp ' + self.defaultInputFileName + ' ' + pathPlusSub)
            os.system('cp ' + self.defaultPBSFileName + ' ' + pathPlusSub)

            # modify pbs file's job name
            # create temporary copy of input file
            curPbsFi = pathPlusSub+'/'+self.defaultPBSFileName
            tempPbsFi = pathPlusSub+'/temp'
            shutil.copy(curPbsFi,tempPbsFi)
            with open(tempPbsFi,'r') as fin:
                with open(curPbsFi,'w') as fout:
                    for line in fin:
                        if '#PBS -N ' in line:
                            fout.write('#PBS -N '+subDirName[1:]+'\n')
                        else:
                            fout.write(line)
            fout.close()
            fin.close()
            os.remove(tempPbsFi)

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

        # inidicate the study has built succefully
        self.buildComplete = True


    def hpcExecute(self,numConcJobs):

        # make sure build method has been called aready
        if not self.buildComplete:
            print('You must run the build method before running the hpcExecute method')
        assert self.buildComplete

        # -----------------------
        # check for correct input
        # -----------------------

        # convert numConcJobs to an integer if it is not already
        numConcJobs = int(numConcJobs)

        # make sure numConcJobs is greater than zero
        if numConcJobs < 1:
            print('0 < numConcJobs <= total number of parameter sets')
        assert numConcJobs > 1

        # make sure numConcJobs is less than the number of parameter sets
        if not (numConcJobs <= self.numOfParamSets):
            print('numConcJobs must be less than the total number of parameter sets.')
            print('for example, if you have two parameters "a" and "b" and each will')
            print('have 3 unique values, then the total number of unique (a,b) pairs')
            print('will be equal to 9, thus yielding a total of 9 total jobs to be')
            print('to be submitted. Therefore numConcJobs must be less than or equal')
            print('to 9.')
        assert numConcJobs <= self.numOfParamSets

        # -----------------------------------------------
        # loop over the list of unique parameter sets and
        # submit them to the HPC
        # -----------------------------------------------

        jobIDs = []
        self.allJobs = []

        # start the first batch of jobs to run simultaneously
        for i in range(numConcJobs):
            # change to the sub-directory to start the job
            os.chdir(self.subDir[i])
            # build the command to submit job to the HPC
            cmd = ['qsub',self.defaultPBSFileName]
            # submit the job and get the job ID
            jID = sp.check_output(cmd)
            # store the job ID in a list
            jobIDs.append(jID.split('.')[0])
            # keep a running list of all job IDs
            self.allJobs.append(jID.split('.')[0])

        # start the rest of the jobs on hold until the first batch finishes
        nextBatch = []
        for id in jobIDs:
            nextBatch.append(id)
        count = 1
        for sd in self.subDir[numConcJobs:]:
            os.chdir(sd)
            jobStr = ':'.join(nextBatch)
            # build the command to submit job to the HPC
            cmd = ['qsub','-W','depend=afterany:'+jobStr,self.defaultPBSFileName]
            print(cmd)
            # submit the job and get the job ID
            jID = sp.check_output(cmd)
            # store the job ID in a list
            jobIDs.append(jID.split('.')[0])
            # update running list of all job IDs
            self.allJobs.append(jID.split('.')[0])
            # make sure job list never grows beyond numConcJobs
            jobIDs.pop(0)
            # update nextBatch
            if (count % numConcJobs) == 0:
                for i in range(numConcJobs):
                    nextBatch[i] = jobIDs[i]
            count += 1

        # -----------------------------------------------
        # write job ID's to the file 'jobIDs.txt'
        # -----------------------------------------------

        # change back to the starting directory
        os.chdir(self.startDir)
        with open('jobIDs.txt','w') as fout:
            for jobID in self.allJobs:
                fout.write(jobID+'\n')
        fout.close()
