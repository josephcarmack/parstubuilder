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

def test_kwargs_init():
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
