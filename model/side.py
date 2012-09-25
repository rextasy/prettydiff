from prettydiff.model.line import Line

class Side(object):
    '''Temporary holder object used by prettydiff to manage the state of one
    side (A or B, in the comparison of A to B) of the current diff chunk.
    An instance of this class is created by the
    prettydiff.model.chunk::Chunk.__init__ method and later used to render the
    chunk information into markup.'''

    # array of data (source code) from the chunk to be rendered for the side
    lines = None

    # the starting line from the chunk for the side
    start = None

    # number of stubs needed to align this side to the other within the chunk
    stubs = None

    def __init__(self, starting_line_number):
        self.lines = []
        self.stubs = 0
        self.start = starting_line_number

    def add_line(self, src, status):
        '''Adds a line of code and its status to the side. The line number is
        automatically calculated.'''
        line = Line(src, status, self.start + len(self.lines) - self.stubs)
        self.lines.append(line)
        return line

    def add_stub(self):
        '''Adds a stub for a line of code to the side. Stubs are used to keep the
        side-by-side diff balanced.'''
        self.lines.append(None)
        self.stubs += 1
