class Line(object):
    '''Temporary holder object used by prettydiff to manage the state of a
    single line of code for one side of a diff chunk. An instance of this class
    is created by the prettydiff.model.side::Side.__init__ method and later
    used to render the chunk information into markup.'''

    # the line of source code
    data = None

    # the line of source code's status (normal, added, removed, modified)
    status = None

    # the line number for this line of code
    line_num = None

    def __init__(self, src, status, line_num):
        self.data = src
        self.status = status
        self.line_num = line_num
