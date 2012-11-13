import prettydiff, sys
from ..model.diff import Diff
from ..model.chunk import Chunk

class DiffParser(object):
    '''Parses a unified diff into an array of diffs which may be passed to a
    prettydiff view class for rendering.'''

    diffs = None

    def __init__(self, diff_lines = []):
        '''Parses the passed array of unified diff lines. The resulting diffs
        may then be passed to a prettydiff view class for rendering.

        :param diff_lines: an array of lines from a unified diff
        '''

        # keep an array of all the diffs processed
        self.diffs = []

        # keep a reference to the diff currently being processed
        self._diff = None

        # create an iterator through the lines of the diff
        self._iter = iter(diff_lines)

        self._removed_queue = []

        # actions invoked by processing the first character in a diff line
        actions = {
            'd': self._start_diff,
            '@': self._start_chunk,
            ' ': self._append_both,
            '-': self._appendA,
            '+': self._appendB
        }

        # parse the lines into one or more diffs, each with one or more chunks;
        # the first character of each line is used to determine which action to
        # take: start a new diff, start new diff chunk, or append to the files
        for line in self._iter:
            if (line[0] in actions):
                actions[line[0]](line)

    def _start_diff(self, line):
        '''Parsing handler starts a new diff.'''

        while True:
            file1info = self._iter.next()
            if 0 == file1info.find("---"): break

        while True:
            file2info = self._iter.next()
            if 0 == file2info.find("+++"): break

#        print "[%s][%s][%s]" % (line, file1info, file2info)
#        sys.exit()

        self._diff = Diff(line, file1info, file2info)
        self.diffs.append(self._diff)

    def _start_chunk(self, line):
        '''Parsing handler starts a new diff -> chunk.'''
        self._diff.chunk = Chunk(line)
        self._diff.chunks.append(self._diff.chunk)

    def _append_both(self, line):
        '''Parsing handler appends the given line to both sides of the diff
        chunk.'''
        data = line[1:]

        self._diff.chunk.A.add_line(data, prettydiff.NORMAL)

        # add stubs to B for each of the remaining items in the remove queue
        for _ in self._removed_queue:
            self._diff.chunk.B.add_stub()

        # clear the remove queue; all remaining lines are proper removes
        self._removed_queue = []

        self._diff.chunk.B.add_line(data, prettydiff.NORMAL)

    def _appendA(self, line):
        '''Parsing handler appends the given line to side A of the diff chunk
        and appends a stub to side B of the diff chunk.'''
        chunk = self._diff.chunk

        lineA = chunk.A.add_line(line[1:], prettydiff.REMOVED)

        # keep a list of lines beginning with '-' to match up against any '+'
        # lines; each '+' line changes the 1st '-' line's status to
        # prettydiff.MODIFIED (see prettydiff.parser.Parser._appendB)
        self._removed_queue.append(lineA)

    def _appendB(self, line):
        '''Parsing handler appends the given line to side B of the diff chunk
        and appends a stub to side A of the diff chunk.'''

        # if the remove queue is empty then this is an added line of code to B
        # which requires a stub for A; if it is not empty, update A's first
        # remove and change its status to modified.
        if not self._removed_queue:
            status = prettydiff.ADDED
            self._diff.chunk.A.add_stub()
        else:
            status = prettydiff.MODIFIED
            self._removed_queue.pop(0).status = status

        self._diff.chunk.B.add_line(line[1:], status)
