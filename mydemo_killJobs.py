import parstubuilder as psb

# instantiate a ParametricStudy object with
# just the name of your study that has already
# been created.

killJobs = psb.ParametricStudy(
        studyName='mydemo'
        )

# run batchDelete method to kill jobs
killJobs.batchDelete()
