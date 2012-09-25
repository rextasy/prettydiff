class ChangeScope(object):
    l_index = None
    r_index = None

    def __init__(self, l_index = None, r_index = None):
        self.l_index = l_index
        self.r_index = r_index

    def copy(self, l_index_offset = 0, r_index_offset = 0):
        '''Returns a new ChangeScope instance using this instance's values
        (calculated along with any supplied offset).'''

        l = None if self.l_index is None else self.l_index + l_index_offset
        r = None if self.r_index is None else self.r_index + r_index_offset

        return ChangeScope(l, r)

    def __str__(self):
        return "{'l_index': %s, 'r_index': %s}" % (self.l_index, self.r_index)
