from asm_compiler import compiler
from instruction_set_parser import is_parser
import unittest

C = compiler.Compiler


class TokenizeLineTestCase(unittest.TestCase):
    """Tests for the _tokenize_line function of the compiler"""

    def test_extraction_no_args(self):
        self.assertEquals({'args': [], 'name': 'HALT'}, C._tokenize_line('HALT'))

    def test_extraction_one_arg(self):
        self.assertEquals({'args': ['.end'], 'name': 'JP'}, C._tokenize_line('JP .end'))

    def test_extraction_with_literal(self):
        self.assertEquals({'args': ['A', '32'], 'name': 'LD'}, C._tokenize_line('LD A, 32'))

    def test_extraction_with_variable(self):
        self.assertEquals({'args': ['A', 'B'], 'name': 'LD'}, C._tokenize_line('LD A, B'))

    def test_complex_extraction(self):
        self.assertEquals({'args': ['A', 'B', '32'], 'name': 'CPLX'},
                          C._tokenize_line('CPLX A, B, 32'))

    def test_extraction_without_optional_space(self):
        self.assertEquals({'args': ['A', 'B'], 'name': 'LD'}, C._tokenize_line('LD A,B'))

    def test_extraction_with_too_many_spaces(self):
        self.assertEquals({'args': ['A', 'B', 'C'], 'name': 'LD'}, C._tokenize_line('LD A  ,  B , C  '))


class TokenizeInstructionTestCase(unittest.TestCase):
    """Tests for the _tokenize_instruction function of the compiler"""

    def test_extraction_no_args(self):
        instr = is_parser.Instruction(0, 1, 'HALT')
        self.assertEquals({'args': [], 'name': 'HALT'}, C._tokenize_instruction(instr))

    def test_extraction_one_arg(self):
        instr = is_parser.Instruction(0, 1, 'INC B')
        self.assertEquals({'args': ['B'], 'name': 'INC'}, C._tokenize_instruction(instr))

    def test_extraction_with_literal(self):
        instr = is_parser.Instruction(0, 2, 'LD A,_$literal')
        self.assertEquals({'args': ['A', '$literal'], 'name': 'LD'}, C._tokenize_instruction(instr))

    def test_extraction_with_address(self):
        instr = is_parser.Instruction(0, 2, 'JP M,_$address')
        self.assertEquals({'args': ['M', '$address'], 'name': 'JP'}, C._tokenize_instruction(instr))

    def test_complex_extraction(self):
        instr = is_parser.Instruction(0, 3, 'CPLX A,_$address, $literal')
        self.assertEquals({'args': ['A', '$address', '$literal'], 'name': 'CPLX'}, C._tokenize_instruction(instr))


class InstructionEncoderTestCase(unittest.TestCase):
    """Tests for the _encode_instruction function of the compiler,
    as well as the _get_binary and _get_object _representation methods"""

    def test_encoding_simple(self):
        instr = is_parser.Instruction(0, 1, 'HALT')
        self.assertEquals([0], C._encode_instruction(instr, []))

    def test_encoding_literal(self):
        instr = is_parser.Instruction(5, 2, 'LD A,_$literal')
        self.assertEquals([5, 7], C._encode_instruction(instr, ['A', '7']))


class FindMatchingInstructionTestCase(unittest.TestCase):
    """Tests for the _find_matching_instruction of the compiler"""

    PA = None

    @classmethod
    def setUpClass(cls):
        cls.PA = is_parser.ProcessorArchitecture()
        cls.PA.INSTRUCTION_SET.append(is_parser.Instruction(0, 1, 'HALT'))
        cls.PA.INSTRUCTION_SET.append(is_parser.Instruction(1, 2, 'LD A,_$literal'))
        cls.PA.INSTRUCTION_SET.append(is_parser.Instruction(2, 1, 'LD A,_B'))
        cls.PA.INSTRUCTION_SET.append(is_parser.Instruction(3, 1, 'LD A,_C'))
        cls.PA.INSTRUCTION_SET.append(is_parser.Instruction(4, 2, 'JP P,_$address'))
        cls.PA.INSTRUCTION_SET.append(is_parser.Instruction(5, 2, 'JP M,_$address'))

    def test_find_single_instruction(self):
        self.assertEquals(self.PA.INSTRUCTION_SET[0],
                          C._find_matching_instruction(self.PA, {'name': 'HALT', 'args': []}))

    def test_find_ambiguous_instruction(self):
        self.assertEquals(self.PA.INSTRUCTION_SET[2],
                          C._find_matching_instruction(self.PA, {'name': 'LD', 'args': ['A', 'B']}))

    def test_find_ambiguous_instruction_with_variable(self):
        self.assertEquals(self.PA.INSTRUCTION_SET[5],
                          C._find_matching_instruction(self.PA, {'name': 'JP', 'args': ['M', '$address']}))


class BinaryToASCIITestCase(unittest.TestCase):
    """Tests for the _binary_to_ASCII function of the compiler"""

    def test_encoding_short_object(self):
        self.assertEquals('0010\n', C._binary_to_ascii([2], 4))

    def test_encoding_large_object(self):
        self.assertEquals('00000010\n00000011\n11111111\n00000111\n', C._binary_to_ascii([2, 3, 255, 7], 8))

class AdjustAddressesTestCase(unittest.TestCase):
    """Tests for the _adjust_addresses function of the compiler"""
    # Todo: Implement some unit tests. Right now there's a few integration tests about this.
    pass

def suite():
    tokenize_line_suite = unittest.TestLoader().loadTestsFromTestCase(TokenizeLineTestCase)
    tokenize_instr_suite = unittest.TestLoader().loadTestsFromTestCase(TokenizeInstructionTestCase)
    instruction_encoder_suite = unittest.TestLoader().loadTestsFromTestCase(InstructionEncoderTestCase)
    findmatching_suite = unittest.TestLoader().loadTestsFromTestCase(FindMatchingInstructionTestCase)
    btascii_suite = unittest.TestLoader().loadTestsFromTestCase(BinaryToASCIITestCase)
    adjustaddress_suite = unittest.TestLoader().loadTestsFromTestCase(AdjustAddressesTestCase)

    return unittest.TestSuite([tokenize_line_suite, tokenize_instr_suite, instruction_encoder_suite,
                               findmatching_suite, btascii_suite, adjustaddress_suite])

