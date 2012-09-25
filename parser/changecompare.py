import re
from .changescope import ChangeScope

class ChangeCompare(object):

    MARKER_CONFIG = {
        'left': '[:LEFT:]',
        'right': '[:RIGHT:]',
        'insert': '[:INSERT:]'
    }

    @staticmethod
    def mark_change(s1, s2, delim = MARKER_CONFIG, ignore_whitespace = True):
        '''Static method returns a 2-tuple containing the two passed strings
        marked up to annotate the change between the two strings.'''

        mark = ChangeCompare._mark

        if ignore_whitespace:
            change = ChangeCompare._scope_change_ignore_whitespace(s1, s2)

            if change['whitespace']:
                s1 = mark(s1, change['head'][0], change['tail'][0], delim)
                s2 = mark(s2, change['head'][1], change['tail'][1], delim)
            else:
                s1 = mark(s1, change['scope'][0], None, delim)
                s2 = mark(s2, change['scope'][1], None, delim)
        else:
            change = ChangeCompare._scope_change(s1, s2)
            s1 = mark(s1, change[0], None, delim)
            s2 = mark(s2, change[1], None, delim)

        return (s1, s2)

    @staticmethod
    def swap_markers(str, new_delim, old_delim = MARKER_CONFIG):
        for pos in ('left', 'right', 'insert'):
            str = str.replace(old_delim[pos], new_delim[pos])
        return str

    @staticmethod
    def _mark(str, scope, scope2 = None, delim = MARKER_CONFIG):

        adjustment = 0

        if scope2:
            str2 = ChangeCompare._mark(str, scope2, None, delim)
            adjustment = len(str2) - len(str)
            str = str2

        if scope.l_index is None:
            return str

        r_pos = len(str) - scope.r_index - adjustment
        l_pos = scope.l_index

        if r_pos == l_pos:
            str = str[:l_pos] + delim['insert'] + str[l_pos:]
        else:
            str = str[:r_pos] + delim['right'] + str[r_pos:]
            str = str[:l_pos] + delim['left'] + str[l_pos:]

        return str

    @staticmethod
    def _diff_index(a, b):
        '''Given two strings returns the index of the character where the two
        strings diverge. Returns -1 if passed equal strings, returns None if
        the strings never diverge (e.g. substring).'''

        # if both strings are equal return 'no change'
        if a==b: return -1

        # if either string is empty the strings diverge at the very front
        if not (a and b): return 0

        _a = len(a)
        _b = len(b)

        # roll through the strings looking for the first unequal character
        for i in range(min(_a, _b)):
            if a[i] != b[i]: return i

        # the strings are unequal and no characters differed (substring)
        return None

    @staticmethod
    def _scope_change(a, b):
        '''Given two strings returns a 2-tuple of ChangeScope objects (one for
        each string a and b) with the index from the left and index from the
        right marking where that string diverges from the other.'''

        l_index = ChangeCompare._diff_index(a, b)

        # if strings are equal, return a no-op scope
        if l_index == -1:
            s = ChangeScope()
            return (s, s)

        # if the strings are unequal and no characters differed then one string
        # is a substring of the other, so the left index is the length of the
        # shorter string
        if l_index is None:
            s = ChangeScope(min(len(a), len(b)), 0)
            return (s, s)

        # find the right index by chopping off the already skipped characters
        # from the front of each string and then reversing the remainder (since
        # diff_index scans left-to-right)
        a_tail = a[l_index:][::-1]
        b_tail = b[l_index:][::-1]
        r_index = ChangeCompare._diff_index(a_tail, b_tail)

        # r_index will be None if the compared tails are unequal but one tail
        # string is a substring of the other tail string
        if r_index is None:
            r_index = min(len(a_tail), len(b_tail))

        s = ChangeScope(l_index, r_index)
        return (s, s)

    @staticmethod
    def _scope_change_ignore_whitespace(a, b):
        '''Given two strings returns 2-tuple of ChangeScope references (one for
        each string) each with the index from the left and index from the right
        of each respective string marking where the strings diverge.

        The first test is done with whitespace stripped from both ends of each
        string. If a change is found within the stripped strings it returns the
        indices adjusted for # of chars stripped.

        If the first test doesn't find a change then then each string's leading
        whitespace and trailing whitespace are inspected for differences. The idea
        is to keep the scope tight by ignoring white space, but identifying the
        white space if that is the only thing that changed.
        '''
        m = re.match('^(\s*)(.*?)(\s*)$', a)
        a_head = m.group(1)
        a_body = m.group(2)
        a_tail = m.group(3)

        m = re.match('^(\s*)(.*?)(\s*)$', b)
        b_head = m.group(1)
        b_body = m.group(2)
        b_tail = m.group(3)

        len_a_head = len(a_head)
        len_a_tail = len(a_tail)
        len_b_head = len(b_head)
        len_b_tail = len(b_tail)

        scope = ChangeCompare._scope_change(a_body, b_body)

        # ideally a change within the non-whitespace was found, so return the same
        # scope for both strings adjusted to skip any leading/trailing whitespace
        if scope[0].l_index is not None:
            return {
                'whitespace': False,
                'scope': [
                    scope[0].copy(len_a_head, len_a_tail),
                    scope[1].copy(len_b_head, len_b_tail)
                ]
            }

        # if the only change is in whitespace, then identify the change in both
        # the leading whitespace (head) and trailing whitespace (tail)

        len_a = len(a)
        len_b = len(b)

        head_scope = ChangeCompare._scope_change(a_head, b_head)
        tail_scope = ChangeCompare._scope_change(a_tail, b_tail)

        return {
            'whitespace': True,
            'head': [
                head_scope[0].copy(0, len_a - len_a_head),
                head_scope[1].copy(0, len_b - len_b_head)
            ],
            'tail': [
                tail_scope[0].copy(len_a - len_a_tail, 0),
                tail_scope[1].copy(len_b - len_b_tail, 0)
            ]
        }
