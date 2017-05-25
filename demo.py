from parstubuilder import ParametricStudy as ps
from lineMod import lineMod as lm
import os

myStudy = ps(
        studyName='mydemo',
        pathToStudy=os.getcwd()+'/',
        defaultInputFileName='input.dat',
        defaultPBSFileName='run.pbs',
        lineMod=lm,
        parametric_info={'N':[56,100,375],'Ez':[0,12,22]}
        )
myStudy.build()
myStudy.hpcExecute(3)
