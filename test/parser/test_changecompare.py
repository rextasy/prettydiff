import random
import unittest
from prettydiff.parser.changecompare import ChangeCompare

class TestChangeCompare(unittest.TestCase):

    MARKER_CONFIG = {
        'left': '[',
        'right': ']',
        'insert': '~'
    }

#    def setUp(self):
#        True

    def test_empty_strings(self):
        a0 = ''
        b0 = ''

        (a1, b1) = ChangeCompare.mark_change(a0, b0, self.MARKER_CONFIG)

        self.assertEqual(a1, a0)
        self.assertEqual(b1, b0)

    def test_all_whitespace(self):
        a0 = ' '
        b0 = '  '

        (a1, b1) = ChangeCompare.mark_change(a0, b0, self.MARKER_CONFIG)

        self.assertEqual(a1, ' ~')
        self.assertEqual(b1, ' [ ]')

    def test_leading_whitespace(self):
        a0 = ' _'
        b0 = '  _'

        (a1, b1) = ChangeCompare.mark_change(a0, b0, self.MARKER_CONFIG)

        self.assertEqual(a1, ' ~_')
        self.assertEqual(b1, ' [ ]_')

    def test_trailing_whitespace(self):
        a0 = '_\t'
        b0 = '_'

        (a1, b1) = ChangeCompare.mark_change(a0, b0, self.MARKER_CONFIG)

        self.assertEqual(a1, '_[\t]')
        self.assertEqual(b1, '_~')

    def test_surrounding_whitespace(self):
        a0 = '\t _ \t'
        b0 = '   _   '

        (a1, b1) = ChangeCompare.mark_change(a0, b0, self.MARKER_CONFIG)

        self.assertEqual(a1, '[\t] _ [\t]')
        self.assertEqual(b1, '[  ] _ [  ]')

    def test_ignored_whitespace(self):
        a0 = '\t X \t'
        b0 = '   Y   '

        (a1, b1) = ChangeCompare.mark_change(a0, b0, self.MARKER_CONFIG)

        self.assertEqual(a1, '\t [X] \t')
        self.assertEqual(b1, '   [Y]   ')

    def test_long_substring(self):
        a0 = '123'
        b0 = '....................................................123'

        (a1, b1) = ChangeCompare.mark_change(a0, b0, self.MARKER_CONFIG)
        #CASE004
        self.assertEqual(a1, '~123')
        self.assertEqual(b1, '[....................................................]123')

    def test_composite_index_problem(self):
        a0 = '.left {'
        b0 = '.left, .right {'

        (a1, b1) = ChangeCompare.mark_change(a0, b0, self.MARKER_CONFIG)

        self.assertEqual(a1, '.left~ {')
        self.assertEqual(b1, '.left[, .right] {')

suite = unittest.TestLoader().loadTestsFromTestCase(TestChangeCompare)
unittest.TextTestRunner(verbosity=2).run(suite)
