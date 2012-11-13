import re
from prettydiff.model.side import Side

class Chunk(object):
    '''Temporary holder object used by prettydiff to manage the state of the
    current diff chunk. An instance of this class is created by the
    prettydiff.parser::Parser._start_chunk method and later used by the
    prettydiff.view.htmlview::HtmlView.render method to render the chunk
    information into markup.'''

    # each diff chunk has two sides that are compared; each of these
    # sides are a reference to a prettydiff.model.side::Side object
    A = None
    B = None

    def __init__(self, chunk_info):
        '''calculates the chunk information from the diff chunk string.

        :param chunk_info: a diff chunk heading line
                           Example:
                                   @@ -19,9 +23,10 @@
                                       |  |  |  |
                              startA --+  |  |  +-- countB
                              countA -----+  +----- startB
        '''

        # parse the chunk information string into startA and startB integers
        m = re.search('^@@ -(\d+)(?:,\d+)? \+(\d+)(?:,\d+)? @@$', chunk_info)
        (startA, startB) = (int(m.group(1)), int(m.group(2)))

        # create a holder object for each side of the diff
        (self.A, self.B) = (Side(startA), Side(startB))
