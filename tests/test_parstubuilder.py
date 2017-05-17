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
