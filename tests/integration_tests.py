from io import StringIO
from asm_compiler import compiler
from input_preprocessor import preprocessor
from instruction_set_parser import is_parser
import unittest


class IntegrationTestCase(unittest.TestCase):
    """Various tests of the system as a whole"""

    def test_basic_file(self):
        source = StringIO()
        architecture = StringIO()
        output = StringIO()

        architecture.write('WORD_SIZE(4)\nINSTRUCTION(0b0000, 1, \'HALT\')')
        source.write('HALT')

        architecture.seek(0)
        source.seek(0)

        processor_architecture = is_parser.InstructionSetParser.parse_file(architecture)
        lines = preprocessor.InputPreprocessor.parse_file(source)
        compiler.Compiler.parse_file(lines, output, processor_architecture, False, True)

        output.seek(0)
        self.assertEquals('0000\n', output.read())

    def test_complex_file(self):
        output = StringIO()

        processor_architecture = is_parser.InstructionSetParser.parse_file('test_architecture.txt')
        lines = preprocessor.InputPreprocessor.parse_file('test_source.txt')
        compiler.Compiler.parse_file(lines, output, processor_architecture, False, True)

        output.seek(0)
        with open('test_expected_output.kobj', 'r') as expected_output:
            self.assertEquals(expected_output.read(), output.read())


def suite():
    integration_suite = unittest.TestLoader().loadTestsFromTestCase(IntegrationTestCase)

    return integration_suite
