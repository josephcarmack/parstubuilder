from parstubuilder import ParametricStudy as ps
import pytest
import os
import shutil
from lineMod import lineMod as myLineMod


# --------------------------
# initialization tests
# --------------------------


def test_no_arg_init():
    myStudy = ps()
    assert myStudy.studyName == None
    assert myStudy.defaultInputFileName == None
    assert myStudy.defaultPBSFileName == None
    assert myStudy.lineMod == None
    assert myStudy.parametric_info == None


def test_all_kwargs_init():
    myStudy = ps(
            studyName='test name',
            defaultInputFileName='input.dat',
            defaultPBSFileName='run.pbs',
            lineMod=myLineMod,
            parametric_info={'par1':[0,1,2],'par2':[3,4,5]}
            )
    assert myStudy.studyName == 'test name'
    assert myStudy.defaultInputFileName == 'input.dat'
    assert myStudy.defaultPBSFileName == 'run.pbs'
    assert myStudy.lineMod == myLineMod
    assert myStudy.parametric_info == {'par1':[0,1,2],'par2':[3,4,5]}


def test_some_kwargs_init():
    myStudy = ps(
            studyName='test name',
            lineMod=myLineMod,
            )
    assert myStudy.studyName == 'test name'
    assert myStudy.lineMod == myLineMod


def test_some_kwargs_random_order_init():
    myStudy = ps(
            lineMod=myLineMod,
            studyName='test name',
            )
    assert myStudy.studyName == 'test name'
    assert myStudy.lineMod == myLineMod


def test_invalid_kwarg_init():
    with pytest.raises(ValueError):
        myStudy = ps(
                invalidKwarg='this is a test'
                )


def test_valid_pbs_file():
    with pytest.raises(AssertionError):
        myStudy = ps(
                studyName='study_name',
                defaultInputFileName='input.dat',
                defaultPBSFileName='tests/invalid.pbs',
                lineMod=myLineMod,
                parametric_info={'par1':[0,1,2],'par2':[3,4,5]}
                )


# --------------------------
# build study tests
# --------------------------


def test_build_initialization():
    myStudy = ps()
    with pytest.raises(AssertionError):
        myStudy.build()


def test_create_study_dir():
    myStudy = ps(
            studyName='study_name',
            defaultInputFileName='input.dat',
            defaultPBSFileName='run.pbs',
            lineMod=myLineMod,
            parametric_info={'par1':[0,1,2],'par2':[3,4,5]}
            )
    try:
        myStudy.build()
    except OSError:
        pass
    existing = os.path.isdir(myStudy._startDir+myStudy.studyName)
    if existing:
        shutil.rmtree(myStudy._startDir+myStudy.studyName)
    assert existing


def test_create_existing_study_dir():
    myStudy = ps(
            studyName='study_name',
            defaultInputFileName='input.dat',
            defaultPBSFileName='run.pbs',
            lineMod=myLineMod,
            parametric_info={'par1':[0,1,2],'par2':[3,4,5]}
            )
    os.makedirs(myStudy._startDir+myStudy.studyName)
    with pytest.raises(OSError):
        myStudy.build()
    shutil.rmtree(myStudy._startDir+myStudy.studyName)


def test_create_study_subdir():
    myStudy = ps(
            studyName='study_name',
            defaultInputFileName='input.dat',
            defaultPBSFileName='run.pbs',
            lineMod=myLineMod,
            parametric_info={'par1':[0,1,2],'par2':[3,4,5]}
            )
    myStudy.build()
    numOfSubDirs = 0
    for p,d,f in os.walk(myStudy._startDir+myStudy.studyName):
        numOfSubDirs += len(d)
    shutil.rmtree(myStudy._startDir+myStudy.studyName)
    assert numOfSubDirs == 9


def test_subdir_file_creation():
    myStudy = ps(
            studyName='study_name',
            defaultInputFileName='input.dat',
            defaultPBSFileName='run.pbs',
            lineMod=myLineMod,
            parametric_info={'par1':[0,1,2],'par2':[3,4,5]}
            )
    myStudy.build()
    numOfFiles = 0
    for p,d,f in os.walk(myStudy._startDir+myStudy.studyName):
        numOfFiles += len(f)
    shutil.rmtree(myStudy._startDir+myStudy.studyName)
    assert numOfFiles == 18


def test_input_file_modification():
    myStudy = ps(
            studyName='study_name',
            defaultInputFileName='input.dat',
            defaultPBSFileName='run.pbs',
            lineMod=myLineMod,
            parametric_info={'a':[0,1,2],'b':[3,4,5]}
            )
    myStudy.build()
    with open(myStudy.studyName+'/a0b3/input.dat','r') as fin:
        for line in fin:
            if 'a' in line:
                good = str(line.split(' = ')[1]) == str(0)+'\n'
                if not good:
                    fin.close()
                    os.system('echo contents of failed input file:')
                    os.system('cat '+myStudy.studyName+'/a0b3/input.dat')
                    shutil.rmtree(myStudy._startDir+myStudy.studyName)
                    assert good
                else:
                    fin.close()
                    shutil.rmtree(myStudy._startDir+myStudy.studyName)
                    break


def test_pbs_file_modification():
    myStudy = ps(
            studyName='study_name',
            defaultInputFileName='input.dat',
            defaultPBSFileName='run.pbs',
            lineMod=myLineMod,
            parametric_info={'a':[0,1,2],'b':[3,4,5]}
            )
    myStudy.build()
    with open('study_name/a0b3/run.pbs') as fin:
        contents = fin.read()
        fin.seek(0)
        for line in fin:
            good = line == '#PBS -N a0b3\n'
            break
    fin.close()
    if not good:
        print('failed pbs file contents:')
        print(contents)
    shutil.rmtree(myStudy._startDir+myStudy.studyName)
    assert good


def test_mulit_jobs_per_node_create_scripts_dir():
    myStudy = ps(
            studyName='study_name',
            defaultInputFileName='input.dat',
            defaultPBSFileName='run.pbs',
            lineMod=myLineMod,
            parametric_info={'a':[0,1,2],'b':[3,4,5]}
            )
    myStudy.multipleJobsPerNode = True
    myStudy.executableName = 'running the executable'
    myStudy.build()
    good = os.path.isdir('study_name/jobScripts')
    if not good:
        print('contents of study directory:')
        os.system('ls study_name')
    shutil.rmtree(myStudy._startDir+myStudy.studyName)
    assert good


def test_multi_jobs_per_node_create_submission_scripts():
    myStudy = ps(
            studyName='study_name',
            defaultInputFileName='input.dat',
            defaultPBSFileName='run.pbs',
            lineMod=myLineMod,
            parametric_info={'a':[0,1,2,3],'b':[4,5,6,7]}
            )
    myStudy.multipleJobsPerNode = True
    myStudy.executableName = 'running the executable'
    myStudy.build()
    good = os.path.isfile('study_name/jobScripts/jobs1-16.pbs')
    if not good:
        os.system('ls study_name/jobScripts')
    shutil.rmtree(myStudy._startDir+myStudy.studyName)
    assert good


def test_multi_jobs_per_node_partial_node_use():
    myStudy = ps(
            studyName='study_name',
            defaultInputFileName='input.dat',
            defaultPBSFileName='run.pbs',
            lineMod=myLineMod,
            parametric_info={'a':[0,1,2,3],'b':[4,5,6,7,8]}
            )
    myStudy.multipleJobsPerNode = True
    myStudy.executableName = 'running the executable'
    myStudy.build()
    good = os.path.isfile('study_name/jobScripts/jobs17-20.pbs')
    if not good:
        os.system('ls study_name/jobScripts')
    shutil.rmtree(myStudy._startDir+myStudy.studyName)
    assert good


# --------------------------
# hpcExecute tests
# --------------------------


def test_hpcExecute_no_argument():
    myStudy = ps()
    with pytest.raises(TypeError):
        myStudy.hpcExecute()


def test_hpcExecute_without_building_study():
    myStudy = ps()
    with pytest.raises(AssertionError):
        myStudy.hpcExecute(3)


# --------------------------
# paramter grouping tests
# --------------------------

def test_modify_input_file_with_param_group():
    aPars = [0,1,2,3]
    bPars = [4,5,6,7]
    myStudy = ps(
            studyName='study_name',
            defaultInputFileName='input.dat',
            defaultPBSFileName='run.pbs',
            lineMod=myLineMod,
            parametric_info={'a-b':[aPars,bPars]}
            )
    myStudy.build()
    with open('study_name/a-b-0-4/input.dat') as fin:
        contents = fin.read()
        fin.seek(0)
        checks = []
        for line in fin:
            if 'a =' in line:
                checks.append(line)
            if 'b =' in line:
                checks.append(line)
    fin.close()
    good = True
    for line in checks:
        if 'a =' in line and line != 'a = 0\n':
            good = False
        if 'b =' in line and line != 'b = 4\n':
            good = False
    if not good:
        print(contents)
    shutil.rmtree(myStudy._startDir+myStudy.studyName)
    assert(good)
