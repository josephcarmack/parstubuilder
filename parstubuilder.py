import os
import shutil
import subprocess as sp

class ParametricStudy:

    def __init__(self,**kwargs):

        self.startDir = os.getcwd()+'/'
        self.numOfParamSets = None
        self.subDir = None
        self.listOfSets = None
        self.buildComplete = False
        self.allJobs = None
        self.studyName = None
        self.defaultInputFileName = None
        self.defaultPBSFileName = None
        self.lineMod = None
        self.parametric_info = None
        self.multipleJobsPerNode = False
        self.executableName = None
        self.coresPerNode = 16
        self.coresPerJob = 1
        self.numNodes = None
        self.leftOverJobs = None

        validKwargs = {
                'studyName':self.studyName,
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





    # build parametric study method
    def build(self):


        # ------------------------------------------
        # check to make sure class members have been
        # initialized properly
        # ------------------------------------------

        classMembers = {
                'studyName':self.studyName,
                'defaultInputFileName':self.defaultInputFileName,
                'defaultPBSFileName':self.defaultPBSFileName,
                'lineMod':self.lineMod,
                'parametric_info':self.parametric_info
                }
        goodInitialization = True
        # make sure essential class attributes have been initialized
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
        # if running more than 1 job per node check to make sure certain
        # attributes have been initialized
        if self.multipleJobsPerNode:
            if self.executableName == None:
                print('must define the executableName attribute with the')
                print('executable file\'s name (string type).')
                goodInitialization = False
        assert goodInitialization

        # -----------------------------
        # create main study directory
        # -----------------------------

        os.makedirs(self.startDir + self.studyName)

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

        # --------------------------------------------------------------------
        # loop over list of unique param sets and create directories and files
        # --------------------------------------------------------------------

        self.subDir = []
        for s in self.listOfSets:

            # create sub directories
            subDirName = '/'
            for param in sorted(s):
                subDirName += str(param)+str(s[param])
            pathPlusSub = self.startDir+self.studyName+subDirName
            self.subDir.append(pathPlusSub)

            os.makedirs(pathPlusSub)

            # populate sub-directory with input file
            os.system('cp ' + self.defaultInputFileName + ' ' + pathPlusSub)

            # modify input file by looping over each parameter to be modified
            for par in sorted(s):
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

            if not self.multipleJobsPerNode:
                # populate sub-directory with pbs file
                os.system('cp ' + self.defaultPBSFileName + ' ' + pathPlusSub)

                # modify pbs file's job name
                # create temporary copy of pbs file
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

        # ------------------------------------
        # Running multiple jobs per node setup
        # ------------------------------------

        if self.multipleJobsPerNode:
            # get the executable command line from the default PBS file
            execCommand = None
            with open(self.defaultPBSFileName) as fin:
                for line in fin:
                    if self.executableName in line:
                        execCommand = line
            fin.close
            # strip off new line character from executable command
            execCommand = execCommand.split('\n')[0]

            # check that the executable command was found in the PBS file
            if execCommand == None:
                print('could not find executable command line in')
                print(self.defaultPBSFileName +'. No instance of')
                print('"'+self.executableName+'" in '+self.defaultPBSFileName+'.')
                raise AssertionError

            # figure out how many nodes are going to be needed
            print('Proceeding with the assumption that each node has '+str(self.coresPerNode)+' cores')
            print('and each job will run on only '+str(self.coresPerJob)+' core(s). If this is not the')
            print('case, restart and define the ParametricStudy attributes')
            print('"coresPerNode" and "coresPerJob" with the appropriate values.')
            jobsPerNode = int(int(self.coresPerNode)/int(self.coresPerJob))
            if jobsPerNode < 1 or jobsPerNode > self.coresPerNode:
                print('invalid value for either "coresPerNode" attribute or "coresPerJob" attribute.')
                raise AssertionError
            self.numNodes = int(int(self.numOfParamSets)/int(jobsPerNode))
            self.leftOverJobs = int(int(self.numOfParamSets)%int(jobsPerNode))

            # create directory for job scripts and populate with needed pbs files
            os.makedirs(self.startDir+self.studyName+'/jobScripts')
            jobCounter = 0
            jstart = 0
            jend = 0
            for i in range(self.numNodes):
                jstart = i*jobsPerNode+1
                jend = (i+1)*jobsPerNode
                jnum = str(jstart)+'-'+str(jend)
                curPbsFi = self.startDir+self.studyName+'/jobScripts/jobs'+jnum+'.pbs'
                os.system('cp '+self.startDir+self.defaultPBSFileName+' '+curPbsFi)

                # alter the pbs script to run jobs assigned it
                with open(self.defaultPBSFileName,'r') as fin:
                    with open(curPbsFi,'w') as fout:
                        for line in fin:
                            if '#PBS -N ' in line:
                                fout.write('#PBS -N jobs'+jnum+'\n')
                            elif self.executableName in line:
                                fout.write('# go to job sub-directories and start jobs then wait\n')
                                writeStart = fout.tell()
                                break
                            else:
                                fout.write(line)

                        # write bash code to pbs file that starts and waits for jobs assigned this file
                        for j in range(jobsPerNode):
                            fout.write('cd '+self.subDir[jobCounter]+'\n')
                            fout.write(execCommand+'&\n')
                            jobCounter += 1
                        fout.write('wait\n')
                        # write the rest of the lines from the default pbs file
                        for line in fin:
                            fout.write(line)
                fin.close()
                fout.close()

            # handle case when using only some cores of the last node
            if self.leftOverJobs > 0:
                jstart = jend + 1
                jend = jend + self.leftOverJobs
                jnum = str(jstart)+'-'+str(jend)
                curPbsFi = self.startDir+self.studyName+'/jobScripts/jobs'+jnum+'.pbs'
                os.system('cp '+self.startDir+self.defaultPBSFileName+' '+curPbsFi)

                # alter the pbs script to run jobs assigned it
                with open(self.defaultPBSFileName,'r') as fin:
                    with open(curPbsFi,'w') as fout:
                        for line in fin:
                            if '#PBS -N ' in line:
                                fout.write('#PBS -N jobs'+jnum+'\n')
                            elif self.executableName in line:
                                fout.write('# go to job sub-directories and start jobs then wait\n')
                                writeStart = fout.tell()
                                break
                            else:
                                fout.write(line)

                        # write bash code to pbs file that starts and waits for jobs assigned this file
                        for j in range(self.leftOverJobs):
                            fout.write('cd '+self.subDir[jobCounter]+'\n')
                            fout.write(execCommand+'&\n')
                            jobCounter += 1
                        fout.write('wait\n')
                        # write the rest of the lines from the default pbs file
                        for line in fin:
                            fout.write(line)
                fin.close()
                fout.close()


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
            print('numConcJobs < 0.')
        assert numConcJobs > 0

        # -----------------------------------------------
        # loop over the list of unique parameter sets and
        # submit them to the HPC
        # -----------------------------------------------

        jobIDs = []
        self.allJobs = []

        if not self.multipleJobsPerNode:
            # make sure numConcJobs is less than the number of parameter sets
            if numConcJobs > self.numOfParamSets:
                print('numConcJobs is more than needed. Adjusting to needed amount:')
                while numConcJobs > self.numOfParamSets:
                    numConcJobs -= 1
                print('changed to numConcJobs='+str(numConcJobs))
            assert numConcJobs <= self.numOfParamSets and numConcJobs > 0

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
            for sd in self.subDir[numConcJobs:]:
                os.chdir(sd)
                jobStr = jobIDs[0]
                # build the command to submit job to the HPC
                cmd = ['qsub','-W','depend=afterany:'+jobStr,self.defaultPBSFileName]
                # submit the job and get the job ID
                jID = sp.check_output(cmd)
                # store the job ID in a list
                jobIDs.append(jID.split('.')[0])
                # update running list of all job IDs
                self.allJobs.append(jID.split('.')[0])
                # make sure job list never grows beyond numConcJobs
                jobIDs.pop(0)
        else:
            # make sure numConcJobs is in valid range
            if self.leftOverJobs > 0:
                self.numNodes += 1
            if numConcJobs > self.numNodes:
                print('numConcJobs is more than needed. Adjusting to needed amount:')
                while numConcJobs > self.numNodes:
                    numConcJobs -= 1
                print('changed to numConcJobs='+str(numConcJobs))
            assert numConcJobs <= self.numNodes and numConcJobs > 0
            # get list of multi-job pbs scripts
            jobScripts = os.listdir(self.startDir+self.studyName+'/jobScripts')
            os.chdir(self.startDir+self.studyName+'/jobScripts')
            # start the first batch of jobs to run simultaneously
            for i in range(numConcJobs):
                # build the command to submit job to the HPC
                cmd = ['qsub',jobScripts[i]]
                # submit the job and get the job ID
                jID = sp.check_output(cmd)
                # store the job ID in a list
                jobIDs.append(jID.split('.')[0])
                # keep a running list of all job IDs
                self.allJobs.append(jID.split('.')[0])

            # start the rest of the jobs on hold until the first batch finishes
            for js in jobScripts[numConcJobs:]:
                jobStr = jobIDs[0]
                # build the command to submit job to the HPC
                cmd = ['qsub','-W','depend=afterany:'+jobStr,js]
                # submit the job and get the job ID
                jID = sp.check_output(cmd)
                # store the job ID in a list
                jobIDs.append(jID.split('.')[0])
                # update running list of all job IDs
                self.allJobs.append(jID.split('.')[0])
                # make sure job list never grows beyond numConcJobs
                jobIDs.pop(0)

        # -----------------------------------------------
        # write job ID's to the file 'jobIDs.txt'
        # -----------------------------------------------

        # change back to the starting directory
        os.chdir(self.startDir+self.studyName)
        with open('jobIDs.txt','w') as fout:
            for jobID in self.allJobs:
                fout.write(jobID+'\n')
        fout.close()


    def batchDelete(self):

        # -----------------------------------------------
        # check that study is defined and valid
        # -----------------------------------------------

        # checking for jobID.txt file existence
        assert os.path.isfile(self.startDir+'/'+self.studyName+'/jobIDs.txt')

        # make sure studyName atribute is defined
        bad = self.studyName == None
        if bad:
            print('must define attribute "studyName" before calling this method.')
            print('the string you pass to the batchDelete method must match the')
            print('"studyName" attribute.')
        assert not bad

        with open(self.startDir+'/'+self.studyName+'/jobIDs.txt') as fin:
            for line in fin:
                jobID = line.split('\n')[0]
                cmd = ['qdel',jobID]
                print('Deleting job with job ID: '+jobID)
                try:
                    cmdReturn = sp.check_output(cmd)
                except Exception as e:
                    print('exception caught: '+ type(e).__name__)
        fin.close()

# lineMod function that works for MESO

def lineMod(line,par,par_value):
    rep_value = str(par_value)+str('\n')
    if par in line:
        orig_value = str(line.split(' = ')[1])
        rep_line = line.replace(orig_value,rep_value)
        return rep_line
    else:
        return None
