from parstubuilder import ParametricStudy as ps
import pytest
import os
import shutil

# --------------------------
# initialization tests
# --------------------------

def test_no_arg_init():
    myStudy = ps()
    assert myStudy.studyName == 'Study Name'
    assert myStudy.pathToStudy == 'path-to-study'
    assert myStudy.defaultInputFileName == 'defaultInputFile.dat'
    assert myStudy.inputFileMod == 'input file modifier executable name'
    assert myStudy.parametric_info == {}

def test_all_kwargs_init():
    myStudy = ps(
            studyName='test name',
            pathToStudy='/path/to/study/',
            defaultInputFileName='mesoGen.py',
            inputFileMod='mesoMod.py',
            parametric_info={'par1':[0,1,2],'par2':[3,4,5]}
            )
    assert myStudy.studyName == 'test name'
    assert myStudy.pathToStudy == '/path/to/study/'
    assert myStudy.defaultInputFileName == 'mesoGen.py'
    assert myStudy.inputFileMod == 'mesoMod.py'
    assert myStudy.parametric_info == {'par1':[0,1,2],'par2':[3,4,5]}

def test_some_kwargs_init():
    myStudy = ps(
            studyName='test name',
            inputFileMod='mesoMod.py',
            pathToStudy='/path/to/study/',
            )
    assert myStudy.studyName == 'test name'
    assert myStudy.pathToStudy == '/path/to/study/'
    assert myStudy.defaultInputFileName == 'defaultInputFile.dat'
    assert myStudy.inputFileMod == 'mesoMod.py'
    assert myStudy.parametric_info == {}

def test_some_kwargs_random_order_init():
    myStudy = ps(
            pathToStudy='/path/to/study/',
            inputFileMod='mesoMod.py',
            studyName='test name',
            )
    assert myStudy.studyName == 'test name'
    assert myStudy.pathToStudy == '/path/to/study/'
    assert myStudy.defaultInputFileName == 'defaultInputFile.dat'
    assert myStudy.inputFileMod == 'mesoMod.py'
    assert myStudy.parametric_info == {}

def test_invalid_kwarg_init():
    with pytest.raises(ValueError):
        myStudy = ps(
                pathToStudy='/path/to/study/',
                invalidKwarg='this is a test'
                )

# --------------------------
# build study tests
# --------------------------

def test_create_study_dir():
    myStudy = ps(
            studyName='study_name',
            pathToStudy='./',
            defaultInputFileName='mesoGen.py',
            inputFileMod='mesoMod.py',
            parametric_info={'par1':[0,1,2],'par2':[3,4,5]}
            )
    myStudy.build()
    existing = os.path.isdir(myStudy.pathToStudy+myStudy.studyName)
    if existing:
        shutil.rmtree(myStudy.pathToStudy+myStudy.studyName)
    assert existing

def test_create_existing_study_dir():
    myStudy = ps(
            studyName='study_name',
            pathToStudy='./',
            defaultInputFileName='mesoGen.py',
            inputFileMod='mesoMod.py',
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
            defaultInputFileName='mesoGen.py',
            inputFileMod='mesoMod.py',
            parametric_info={'par1':[0,1,2],'par2':[3,4,5]}
            )
    myStudy.build()
    numOfSubDirs = 0
    for p,d,f in os.walk(myStudy.pathToStudy+myStudy.studyName):
        numOfSubDirs += len(d)
    shutil.rmtree(myStudy.pathToStudy+myStudy.studyName)
    assert numOfSubDirs == 9
