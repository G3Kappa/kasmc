from instruction_set_parser import is_parser
import unittest

ISP = is_parser.InstructionSetParser


class HexToDecimalTestCase(unittest.TestCase):
    """Tests for the hexadecimal part of the _replace_numerals function"""

    def test_simple_literal(self):
        self.assertEquals('2', ISP._replace_numerals('0x0002'))

    def test_uppercase_literal(self):
        self.assertEquals('243', ISP._replace_numerals('0XF3'))

    def test_lowercase_literal(self):
        self.assertEquals('31', ISP._replace_numerals('0x1f'))

    def test_mixedcase_literal(self):
        self.assertEquals('175', ISP._replace_numerals('0xaF'))

    def test_random_literal_position(self):
        self.assertEquals('FIERO69 VERY FIERO', ISP._replace_numerals('FIERO0x45 VERY FIERO'))

    def test_complex_scenario(self):
        self.assertEquals('FIERO69 SPACE VERY FIERO 84', ISP._replace_numerals('FIERO0x45 SPACE VERY FIERO 0X54'))


class BinaryToDecimalTestCases(unittest.TestCase):
    """Tests for the binary part of the _replace_numerals function"""

    def test_leading_zeroes(self):
        self.assertEquals('1', ISP._replace_numerals('0b0001'))

    def test_trailing_zeroes(self):
        self.assertEquals('4', ISP._replace_numerals('0b100'))

    def test_uppercase_literal(self):
        self.assertEquals('6', ISP._replace_numerals('0B110'))

    def test_random_literal_position(self):
        self.assertEquals('FIERO69 VERY FIERO', ISP._replace_numerals('FIERO0b1000101 VERY FIERO'))

    def test_complex_scenario(self):
        self.assertEquals('FIERO1 SPACE VERY FIERO 2', ISP._replace_numerals('FIERO0b01 SPACE VERY FIERO 0b10'))


class KeywordTestCases(unittest.TestCase):
    """Tests for the _parse_line function"""
    PA = None

    def setUp(self):
        self.PA = is_parser.ProcessorArchitecture()

    # Binary and hex tests not performed since the conversion is performed before keywords are parsed
    def test_word_size_regular(self):
        ISP._parse_line(0, 'WORD_SIZE(6)', self.PA)
        self.assertEquals(6, self.PA.WORD_SIZE)

    def test_word_size_random_spacing(self):
        ISP._parse_line(0, '  WORD_SIZE (  16  ) ', self.PA)
        self.assertEquals(16, self.PA.WORD_SIZE)

    def test_instruction_regular(self):
        ISP._parse_line(0, 'INSTRUCTION(1, 1, \'LD B,_A\')', self.PA)
        expected = is_parser.Instruction(1, 1, 'LD B,_A')
        self.assertEquals(expected, self.PA.INSTRUCTION_SET[-1])

    def test_instruction_random_spacing(self):
        ISP._parse_line(0, '  INSTRUCTION  (5  , 2  , \'JP M,_$address\'  )', self.PA)
        expected = is_parser.Instruction(5, 2, 'JP M,_$address')
        self.assertEquals(expected, self.PA.INSTRUCTION_SET[-1])


def suite():
    htd_suite = unittest.TestLoader().loadTestsFromTestCase(HexToDecimalTestCase)
    btd_suite = unittest.TestLoader().loadTestsFromTestCase(BinaryToDecimalTestCases)
    keyword_suite = unittest.TestLoader().loadTestsFromTestCase(KeywordTestCases)

    return unittest.TestSuite([htd_suite, btd_suite, keyword_suite])