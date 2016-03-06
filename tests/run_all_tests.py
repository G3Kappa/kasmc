from tests import parser_tests
from tests import compiler_tests
from tests import preprocessor_tests
from tests import integration_tests
import unittest


def suite():
    return unittest.TestSuite([parser_tests.suite(), preprocessor_tests.suite(), compiler_tests.suite(), integration_tests.suite()])

run_all_suite = suite()

if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(run_all_suite)
