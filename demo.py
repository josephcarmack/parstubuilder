import parstubuilder as psb
import os

# instantiate a ParametricStudy object
myStudy = psb.ParametricStudy(
        studyName='mydemo',
        defaultInputFileName='input.dat',
        defaultPBSFileName='run.pbs',
        lineMod=psb.lineMod,
        parametric_info={
            'N':[56,100,375,400,500],
            'Ez':[0,12,22,30,41]
            }
        )

# uncomment next two lines to test running multiple jobs per node
# myStudy.multipleJobsPerNode = True
# myStudy.executableName = 'sleep'

# build the study directory structure and populate with
# modified input files and job submission scripts
myStudy.build()

# submit jobs to the HPC cluster
jobs_to_run_concurrently = 3
myStudy.hpcExecute(jobs_to_run_concurrently)
