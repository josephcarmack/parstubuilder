from parstubuilder import ParametricStudy as ps
import pytest

# --------------------------
# initialization tests
# --------------------------

def test_no_arg_init():
    myStudy = ps()
    assert myStudy.studyName == 'Study Name'
    assert myStudy.pathToStudy == 'path-to-study'
    assert myStudy.inputFileGen == 'input file generator executable name'
    assert myStudy.inputFileMod == 'input file modifier executable name'
    assert myStudy.parametric_info == {}

def test_all_kwargs_init():
    myStudy = ps(
            studyName='test name',
            pathToStudy='/path/to/study/',
            inputFileGen='mesoGen.py',
            inputFileMod='mesoMod.py',
            parametric_info={'par1':[0,1,2],'par2':[3,4,5]}
            )
    assert myStudy.studyName == 'test name'
    assert myStudy.pathToStudy == '/path/to/study/'
    assert myStudy.inputFileGen == 'mesoGen.py'
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
    assert myStudy.inputFileGen == 'input file generator executable name'
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
    assert myStudy.inputFileGen == 'input file generator executable name'
    assert myStudy.inputFileMod == 'mesoMod.py'
    assert myStudy.parametric_info == {}

def test_invalid_kwarg_init():
    with pytest.raises(ValueError):
        myStudy = ps(
                pathToStudy='/path/to/study/',
                invalidKwarg='this is a test'
                )
