from input_preprocessor import preprocessor
import unittest

PP = preprocessor.InputPreprocessor


class RemoveCommentsTestCase(unittest.TestCase):
    """Tests for the _remove_comments function of the preprocessor"""

    def test_simple_line(self):
        self.assertEquals('LD A, B  ', PP._remove_comments('LD A, B  ; Copies B into A'))

    def test_line_with_multiple_semicolons(self):
        self.assertEquals('LD A, B  ', PP._remove_comments('LD A, B  ; C;opies B;; into A;'))


class RemoveWhitespaceTestCase(unittest.TestCase):
    """Tests for the _remove_trailing_whitespace function of the preprocessor"""

    def test_simple_line(self):
        self.assertEquals('LD A, B', PP._strip_trailing_whitespace('   LD A, B  '))

    def test_line_with_tabs(self):
        self.assertEquals('LD A, B', PP._strip_trailing_whitespace('\tLD A, B\t'))

    def test_mixed_line(self):
        self.assertEquals('label:', PP._strip_trailing_whitespace('   label:\t'))


class LabelTestCase(unittest.TestCase):
    """Tests for the _is_label_defined, _extract_label and _replace_label_usage functions of the preprocessor"""

    def test_is_label_defined_simple(self):
        self.assertEquals(True, PP._is_label_defined('fiero:'))

    def test_is_label_defined_complex(self):
        self.assertEquals(True, PP._is_label_defined('fiero: code which should not be here'))

    def test_extract_label_correct(self):
        self.assertEquals('fiero', PP._extract_label('fiero:'))

    def test_extract_label_wrong(self):
        self.assertEquals(None, PP._extract_label('fiero: code which should not be here'))

    def test_replace_label_usage(self):
        self.assertEquals('JP M, 10', PP._replace_label_usage('JP M, fiero', {'fiero': 10}))


def suite():
    remove_comments_suite = unittest.TestLoader().loadTestsFromTestCase(RemoveCommentsTestCase)
    remove_whitespace_suite = unittest.TestLoader().loadTestsFromTestCase(RemoveWhitespaceTestCase)
    label_suite = unittest.TestLoader().loadTestsFromTestCase(LabelTestCase)

    return unittest.TestSuite([remove_comments_suite, remove_whitespace_suite, label_suite])
