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
    assert myStudy.pathToStudy == None
    assert myStudy.defaultInputFileName == None
    assert myStudy.defaultPBSFileName == None
    assert myStudy.lineMod == None
    assert myStudy.simExecute == None
    assert myStudy.parametric_info == None

def test_all_kwargs_init():
    myStudy = ps(
            studyName='test name',
            pathToStudy='/path/to/study/',
            defaultInputFileName='input.dat',
            defaultPBSFileName='run.pbs',
            lineMod=myLineMod,
            simExecute='meso',
            parametric_info={'par1':[0,1,2],'par2':[3,4,5]}
            )
    assert myStudy.studyName == 'test name'
    assert myStudy.pathToStudy == '/path/to/study/'
    assert myStudy.defaultInputFileName == 'input.dat'
    assert myStudy.defaultPBSFileName == 'run.pbs'
    assert myStudy.lineMod == myLineMod
    assert myStudy.parametric_info == {'par1':[0,1,2],'par2':[3,4,5]}

def test_some_kwargs_init():
    myStudy = ps(
            studyName='test name',
            lineMod=myLineMod,
            pathToStudy='/path/to/study/',
            )
    assert myStudy.studyName == 'test name'
    assert myStudy.pathToStudy == '/path/to/study/'
    assert myStudy.lineMod == myLineMod

def test_some_kwargs_random_order_init():
    myStudy = ps(
            pathToStudy='/path/to/study/',
            lineMod=myLineMod,
            studyName='test name',
            )
    assert myStudy.studyName == 'test name'
    assert myStudy.pathToStudy == '/path/to/study/'
    assert myStudy.lineMod == myLineMod

def test_invalid_kwarg_init():
    with pytest.raises(ValueError):
        myStudy = ps(
                pathToStudy='/path/to/study/',
                invalidKwarg='this is a test'
                )

def test_valid_pbs_file():
    with pytest.raises(AssertionError):
        myStudy = ps(
                studyName='study_name',
                pathToStudy='./',
                defaultInputFileName='input.dat',
                defaultPBSFileName='tests/invalid.pbs',
                lineMod=myLineMod,
                simExecute='meso',
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
            pathToStudy='./',
            defaultInputFileName='input.dat',
            defaultPBSFileName='run.pbs',
            lineMod=myLineMod,
            simExecute='meso',
            parametric_info={'par1':[0,1,2],'par2':[3,4,5]}
            )
    try:
        myStudy.build()
    except OSError:
        pass
    existing = os.path.isdir(myStudy.pathToStudy+myStudy.studyName)
    if existing:
        shutil.rmtree(myStudy.pathToStudy+myStudy.studyName)
    assert existing

def test_create_existing_study_dir():
    myStudy = ps(
            studyName='study_name',
            pathToStudy='./',
            defaultInputFileName='input.dat',
            defaultPBSFileName='run.pbs',
            lineMod=myLineMod,
            simExecute='meso',
            parametric_info={'par1':[0,1,2],'par2':[3,4,5]}
            )
    os.makedirs(myStudy.pathToStudy+myStudy.studyName)
    try:
        myStudy.build()
    except OSError:
        pass
    existing = os.path.isdir(myStudy.pathToStudy+myStudy.studyName+'1')
    shutil.rmtree(myStudy.pathToStudy+myStudy.studyName)
    if existing:
        shutil.rmtree(myStudy.pathToStudy+myStudy.studyName+'1')
    assert existing


def test_create_study_subdir():
    myStudy = ps(
            studyName='study_name',
            pathToStudy='./',
            defaultInputFileName='input.dat',
            defaultPBSFileName='run.pbs',
            lineMod=myLineMod,
            simExecute='meso',
            parametric_info={'par1':[0,1,2],'par2':[3,4,5]}
            )
    myStudy.build()
    numOfSubDirs = 0
    for p,d,f in os.walk(myStudy.pathToStudy+myStudy.studyName):
        numOfSubDirs += len(d)
    shutil.rmtree(myStudy.pathToStudy+myStudy.studyName)
    assert numOfSubDirs == 9

def test_subdir_file_creation():
    myStudy = ps(
            studyName='study_name',
            pathToStudy='./',
            defaultInputFileName='input.dat',
            defaultPBSFileName='run.pbs',
            lineMod=myLineMod,
            simExecute='meso',
            parametric_info={'par1':[0,1,2],'par2':[3,4,5]}
            )
    # create fake default input file, psb file, and simulation executable
    myStudy.build()
    numOfInputFiles = 0
    for p,d,f in os.walk(myStudy.pathToStudy+myStudy.studyName):
        numOfInputFiles += len(f)
    shutil.rmtree(myStudy.pathToStudy+myStudy.studyName)
    assert numOfInputFiles == 27

def test_input_file_modification():
    myStudy = ps(
            studyName='study_name',
            pathToStudy='./',
            defaultInputFileName='input.dat',
            defaultPBSFileName='run.pbs',
            lineMod=myLineMod,
            simExecute='meso',
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
                    shutil.rmtree(myStudy.pathToStudy+myStudy.studyName)
                    assert good
                else:
                    fin.close()
                    shutil.rmtree(myStudy.pathToStudy+myStudy.studyName)
                    break

def test_pbs_file_modification():
    myStudy = ps(
            studyName='study_name',
            pathToStudy='./',
            defaultInputFileName='input.dat',
            defaultPBSFileName='run.pbs',
            lineMod=myLineMod,
            simExecute='meso',
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
    shutil.rmtree(myStudy.pathToStudy+myStudy.studyName)
    assert good

# --------------------------
# submit batch job tests
# --------------------------

