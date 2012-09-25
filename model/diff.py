import re
from prettydiff.model.chunk import Chunk

class Diff(object):
    '''Temporary holder object used by prettydiff to manage the state of the
    diff. An instance of this class is created by the
    prettydiff.parser::Parser._start_chunk method and later used by the
    prettydiff.view.htmlview::HtmlView.render method to render the chunk
    information into markup.'''

    # the name of the file being processed for differences
    file = None

    # reference to the prettydiff.model.chunk::Chunk object being modified
    chunk = None

    # array of prettydiff.model.chunk::Chunk objects which hold the diff chunks
    chunks = None

    # the mercurial rev of the first file
    revA = None

    # whether the first file existed before this diff
    existsA = None

    # the timestamp of the first file
    timestampA = None

    # the mercurial rev of the second file
    revB = None

    # whether the second file existed before this diff
    existsB = None

    # the timestamp of the second file
    timestampB = None

    def __init__(self, rev, file1info, file2info):
        '''Parses the first three lines of a new diff.'''

        # parse each revision and the file name; example:
        #     diff -r a15d7522d7a7 -r 55eb5a4d44aa resources/main.js

        (_, self.revA, self.revB, self.file) = re.split('diff -r | -r | ', rev.strip())

        # parse file 1's timestamp and test whether it existed before; example:
        #     --- /dev/null	Thu Jan 01 00:00:00 1970 +0000
        (fileinfo, self.timestampA) = re.split('\t', file1info.strip())
        self.existsA = self._exists(fileinfo)

        # parse file 2's timestamp and test whether it exists after; example:
        #    +++ b/resources/main.js	Sun Jul 15 23:19:27 2012 -0500
        (fileinfo, self.timestampB) = re.split('\t', file2info.strip())
        self.existsB = self._exists(fileinfo)

        # initialize the list of chunks
        self.chunks = []

    def _exists(self, f):
        return not f.endswith('/dev/null')

    def next_chunk(self, line):
        '''Appends the given line to the chunks list while establishing a
        reference to the most recently created chunk.'''
        self.chunk = Chunk(line)
        self.chunks.append(self.chunk)
