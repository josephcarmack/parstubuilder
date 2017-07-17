import os
import shutil
import subprocess as sp

class ParametricStudy:

    def __init__(self,**kwargs):
        """Initialize the parametric study with appropriate values."""
        # "public" members
        self.studyName = None
        self.defaultInputFileName = None
        self.defaultPBSFileName = None
        self.lineMod = None
        self.parametric_info = None
        self.multipleJobsPerNode = False
        self.executableName = None
        self.coresPerNode = 16
        self.coresPerJob = 1
        # "private" members
        self._startDir = os.getcwd()+'/'
        self._numOfParamSets = None
        self._subDir = None
        self._subDirName = None
        self._listOfSets = None
        self._buildComplete = False
        self._allJobs = None
        self._execCommand = None
        self._jobsPerNode = None
        self._numNodes = None
        self._leftOverJobs = None

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






    # -----------------------------------------------
    # "PRIVATE" methods
    # -----------------------------------------------




    def _checkBuildInit(self):
        """ Check to make sure that the build method was initialized properly."""
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
        return goodInitialization





    def _calcNumUniqueParamSets(self):
        """Calculate the number of unique parameter sets in the parametric study."""
        # calculate the total number of unique parameter sets
        self._numOfParamSets = 1
        for k in sorted(self.parametric_info):
            # check for grouped parameters
            if type(self.parametric_info[k][0]) == list:
                self._numOfParamSets *= len(self.parametric_info[k][0])
            else:
                self._numOfParamSets *= len(self.parametric_info[k])

        # make a list that holds a dictionary for each unique parameter set
        container = self.parametric_info.copy()
        for k in container:
            container[k] = 0
        self._listOfSets = []
        for i in range(self._numOfParamSets):
            self._listOfSets.append(container.copy())

        # calculate each unique parameter set
        skip = 1
        # iterate over each parameter or group of parameters in parametric_info
        for p in sorted(self.parametric_info):
            # grouped parameter values are stored in parametric_info as a list of lists.
            # i.e. one list for each grouped parameter
            if type(self.parametric_info[p][0])==list:
                numParValues = len(self.parametric_info[p][0])
            else:
                numParValues = len(self.parametric_info[p])
            val_i =0
            for i, pSet in enumerate(self._listOfSets):
                if type(self.parametric_info[p][0])==list:
                    pSet[p] = []
                    for grpPar in self.parametric_info[p]:
                        pSet[p].append(grpPar[val_i])
                else:
                    pSet[p] = self.parametric_info[p][val_i]
                if i%skip == 0:
                    val_i += 1
                if val_i == numParValues:
                    val_i = 0
            skip *= numParValues

        # sort the list of parameter sets
        self._listOfSets.sort(key=self._specialSort)





    def _specialSort(self,dic):
        """special sort function for sorting _listOfSets."""
        crit = []
        mykeys = sorted(dic.keys())
        for key in mykeys:
            crit.append(dic[key])
        return tuple(crit)





    def _createDirStructure(self):
        """Create the main study directory and a sub-directory for each parameter set."""
        # make the main study directory
        os.makedirs(self._startDir + self.studyName)

        # create sub directory names
        self._subDir = []
        self._subDirName = []
        for s in self._listOfSets:
            name = ''
            for param in sorted(s):
                # check for grouped parameters
                if type(s[param]) == list:
                    name += str(param)
                    for val in s[param]:
                        name += '-'+str(val)
                else:
                    name += str(param)+str(s[param])
            # create path to sub-directory
            pathPlusSub = self._startDir+self.studyName+'/'+name
            # save sub-directory name and path for later use
            self._subDirName.append(name)
            self._subDir.append(pathPlusSub)
            # create the sub-directory
            os.makedirs(pathPlusSub)





    def _modInputFile(self,param,value,curInFi):
        """Uses lineMod function to modify input file parameters."""
        # create temporary copy of input file
        tempInFi = os.getcwd()+'/temp'
        shutil.copy(curInFi,tempInFi)
        # read from temp and write modified version to original
        with open(tempInFi,'r') as fin:
            with open(curInFi,'w') as fout:
                print(param,value)
                print('temp:')
                print(fin.read())
                fin.seek(0)
                for line in fin:
                    if param in line:
                        print('found param, now lets modify it:')
                        print('line =',line)
                        modifiedLine = self.lineMod(line,param,value)
                        print('modify to:',modifiedLine)
                        print('-------------------')
                        fout.write(modifiedLine)
                    else:
                        fout.write(line)
        fout.close()
        fin.close()
        os.remove(tempInFi)






    def _createInputFiles(self):
        """Copy default input file to sub-directories and modify each one accordingly."""
        for i, s in enumerate(self._listOfSets):
            # populate sub-directory with input file
            os.system('cp ' + self.defaultInputFileName + ' ' + self._subDir[i])
            # input file in current sub-directory
            inputFile = self._subDir[i]+'/'+self.defaultInputFileName
            
            print(s)
            # modify input file by looping over each parameter to be modified
            for par in sorted(s):
                # check for grouped parameters
                if type(s[par])==list:
                    paramNames = par.split('-')
                    # check that grouped parameters were grouped with assumed syntax
                    assert(len(paramNames)==len(s[par]))
                    # modify each of the grouped params in the input file
                    for n,val in enumerate(s[par]):
                        self._modInputFile(paramNames[n],val,inputFile)
                else:
                    # change input file for single non-grouped parameter
                    self._modInputFile(par,s[par],inputFile)





    def _setupJobScripts(self):
        """Create job scripts for jobs that use 1 or more node."""
        # create a job script for each unique parameter set
        for i, s in enumerate(self._listOfSets):
            # populate sub-directory with pbs file
            os.system('cp ' + self.defaultPBSFileName + ' ' + self._subDir[i])

            # modify pbs file's job name
            # create temporary copy of pbs file
            curPbsFi = self._subDir[i]+'/'+self.defaultPBSFileName
            tempPbsFi = self._subDir[i]+'/temp'
            shutil.copy(curPbsFi,tempPbsFi)
            with open(tempPbsFi,'r') as fin:
                with open(curPbsFi,'w') as fout:
                    for line in fin:
                        if '#PBS -N ' in line:
                            fout.write('#PBS -N '+self._subDirName[i]+'\n')
                        else:
                            fout.write(line)
            fout.close()
            fin.close()
            os.remove(tempPbsFi)





    def _findExecCommand(self):
        "Finds the executable command in the default pbs script."""
        # get the executable command line from the default PBS file
        with open(self.defaultPBSFileName) as fin:
            for line in fin:
                if self.executableName in line:
                    self._execCommand = line
        fin.close
        # strip off new line character from executable command
        self._execCommand = self._execCommand.split('\n')[0]

        # check that the executable command was found in the PBS file
        if self._execCommand == None:
            print('could not find executable command line in')
            print(self.defaultPBSFileName +'. No instance of')
            print('"'+self.executableName+'" in '+self.defaultPBSFileName+'.')
            return False
        else:
            return True





    def _calcNumNodesNeeded(self):
        """Calculate how many nodes are needed for the multiple jobs per case."""
        print('Proceeding with the assumption that each node has '+str(self.coresPerNode)+' cores')
        print('and each job will run on only '+str(self.coresPerJob)+' core(s). If this is not the')
        print('case, restart and define the ParametricStudy attributes')
        print('"coresPerNode" and "coresPerJob" with the appropriate values.')
        self._jobsPerNode = int(int(self.coresPerNode)/int(self.coresPerJob))
        if self._jobsPerNode < 1 or self._jobsPerNode > self.coresPerNode:
            print('invalid value for either "coresPerNode" attribute or "coresPerJob" attribute.')
            raise AssertionError
        self._numNodes = int(int(self._numOfParamSets)/int(self._jobsPerNode))
        self._leftOverJobs = int(int(self._numOfParamSets)%int(self._jobsPerNode))





    def _setupMultipleJobsPerNode(self):
        """Create job scripts that run more than one job per node."""
        # create directory for job scripts and populate with needed pbs files
        os.makedirs(self._startDir+self.studyName+'/jobScripts')
        jobCounter = 0
        jstart = 0
        jend = 0
        for i in range(self._numNodes):
            jstart = i*self._jobsPerNode+1
            jend = (i+1)*self._jobsPerNode
            jnum = str(jstart)+'-'+str(jend)
            curPbsFi = self._startDir+self.studyName+'/jobScripts/jobs'+jnum+'.pbs'
            os.system('cp '+self._startDir+self.defaultPBSFileName+' '+curPbsFi)

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
                    for j in range(self._jobsPerNode):
                        fout.write('cd '+self._subDir[jobCounter]+'\n')
                        fout.write(self._execCommand+'&\n')
                        jobCounter += 1
                    fout.write('wait\n')
                    # write the rest of the lines from the default pbs file
                    for line in fin:
                        fout.write(line)
            fin.close()
            fout.close()

        return jend,jobCounter




        
    def _handleLeftOverJobs(self,jend,jobCounter):
        """Handle setup last node when their are left over jobs that do not fill an entire node."""
        print('jend='+str(jend))
        jstart = jend + 1
        jend = jend + self._leftOverJobs
        jnum = str(jstart)+'-'+str(jend)
        curPbsFi = self._startDir+self.studyName+'/jobScripts/jobs'+jnum+'.pbs'
        os.system('cp '+self._startDir+self.defaultPBSFileName+' '+curPbsFi)

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
                for j in range(self._leftOverJobs):
                    fout.write('cd '+self._subDir[jobCounter]+'\n')
                    fout.write(self._execCommand+'&\n')
                    jobCounter += 1
                fout.write('wait\n')
                # write the rest of the lines from the default pbs file
                for line in fin:
                    fout.write(line)
        fin.close()
        fout.close()





    def _checkHpcExecInit(self,numConcJobs):
        """Make sure study was initialized correctly for running the hpcExecute method."""
        # make sure build method has been called aready
        if not self._buildComplete:
            print('You must run the build method before running the hpcExecute method')
        assert self._buildComplete

        # check for correct input
        if numConcJobs < 1:
            print('numConcJobs < 0.')
        # convert numConcJobs to an integer if it is not already
        numConcJobs = int(numConcJobs)
        assert numConcJobs > 0





    def _launchJobs(self,numConcJobs):
        """Launches 1 or more jobs per node on the HPC using qsub."""
        jobIDs = []
        # make sure numConcJobs is less than the number of parameter sets
        if numConcJobs > self._numOfParamSets:
            print('numConcJobs is more than needed. Adjusting to needed amount:')
            while numConcJobs > self._numOfParamSets:
                numConcJobs -= 1
            print('changed to numConcJobs='+str(numConcJobs))
        assert numConcJobs <= self._numOfParamSets and numConcJobs > 0

        # start the first batch of jobs to run simultaneously
        for i in range(numConcJobs):
            # change to the sub-directory to start the job
            os.chdir(self._subDir[i])
            # build the command to submit job to the HPC
            cmd = ['qsub',self.defaultPBSFileName]
            # submit the job and get the job ID
            jID = sp.check_output(cmd)
            # store the job ID in a list
            jobIDs.append(jID.split('.')[0])
            # keep a running list of all job IDs
            self._allJobs.append(jID.split('.')[0])

        # start the rest of the jobs on hold until the first batch finishes
        for sd in self._subDir[numConcJobs:]:
            os.chdir(sd)
            jobStr = jobIDs[0]
            # build the command to submit job to the HPC
            cmd = ['qsub','-W','depend=afterany:'+jobStr,self.defaultPBSFileName]
            # submit the job and get the job ID
            jID = sp.check_output(cmd)
            # store the job ID in a list
            jobIDs.append(jID.split('.')[0])
            # update running list of all job IDs
            self._allJobs.append(jID.split('.')[0])
            # make sure job list never grows beyond numConcJobs
            jobIDs.pop(0)





    def _launchMultiJobsPerNode(self,numConcJobs):
        """Launches multiple jobs per node on the HPC using qsub."""
        jobIDs = []
        # make sure numConcJobs is in valid range
        if self._leftOverJobs > 0:
            self._numNodes += 1
        if numConcJobs > self._numNodes:
            print('numConcJobs is more than needed. Adjusting to needed amount:')
            while numConcJobs > self._numNodes:
                numConcJobs -= 1
            print('changed to numConcJobs='+str(numConcJobs))
        assert numConcJobs <= self._numNodes and numConcJobs > 0
        # get list of multi-job pbs scripts
        jobScripts = os.listdir(self._startDir+self.studyName+'/jobScripts')
        os.chdir(self._startDir+self.studyName+'/jobScripts')
        # start the first batch of jobs to run simultaneously
        for i in range(numConcJobs):
            # build the command to submit job to the HPC
            cmd = ['qsub',jobScripts[i]]
            # submit the job and get the job ID
            jID = sp.check_output(cmd)
            # store the job ID in a list
            jobIDs.append(jID.split('.')[0])
            # keep a running list of all job IDs
            self._allJobs.append(jID.split('.')[0])

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
            self._allJobs.append(jID.split('.')[0])
            # make sure job list never grows beyond numConcJobs
            jobIDs.pop(0)







    # -----------------------------------------------
    # "PUBLIC" METHODS
    # -----------------------------------------------





    def build(self):
        """Build the parametric study directories and files."""
        assert(self._checkBuildInit())
        self._calcNumUniqueParamSets()
        self._createDirStructure()
        self._createInputFiles()
        if not self.multipleJobsPerNode:
            self._setupJobScripts()
        else:
            assert(self._findExecCommand())
            self._calcNumNodesNeeded()
            je,jc = self._setupMultipleJobsPerNode()
            if self._leftOverJobs > 0:
                self._handleLeftOverJobs(je,jc)
        self._buildComplete = True





    def hpcExecute(self,numConcJobs):
        """Start parametric study jobs on the HPC using the "qsub" command."""
        self._checkHpcExecInit(numConcJobs)
        self._allJobs = []
        if not self.multipleJobsPerNode:
            self._launchJobs(numConcJobs)
        else:
            self._launchMultiJobsPerNode(numConcJobs)

        # change back to the starting directory
        os.chdir(self._startDir+self.studyName)
        # write job IDs to a file in case they need to be deleted later
        with open('jobIDs.txt','w') as fout:
            for jobID in self._allJobs:
                fout.write(jobID+'\n')
        fout.close()





    def batchDelete(self):
        """Delete all the jobs running on the HPC for a given parametric study."""
        # checking for jobID.txt file existence
        assert os.path.isfile(self._startDir+'/'+self.studyName+'/jobIDs.txt')

        # make sure studyName atribute is defined
        bad = self.studyName == None
        if bad:
            print('must define attribute "studyName" before calling this method.')
            print('the string you pass to the batchDelete method must match the')
            print('"studyName" attribute.')
        assert not bad

        with open(self._startDir+'/'+self.studyName+'/jobIDs.txt') as fin:
            for line in fin:
                jobID = line.split('\n')[0]
                cmd = ['qdel',jobID]
                print('Deleting job with job ID: '+jobID)
                try:
                    cmdReturn = sp.check_output(cmd)
                except Exception as e:
                    print('exception caught: '+ type(e).__name__)
        fin.close()






# -----------------------------------------------
# Functions that are not class methods
# -----------------------------------------------





def lineMod(line,par,par_value):
    rep_value = str(par_value)+str('\n')
    if par in line:
        orig_value = str(line.split(' = ')[1])
        rep_line = line.replace(orig_value,rep_value)
        return rep_line
    else:
        return None
