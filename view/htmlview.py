from itertools import izip
import prettydiff
from prettydiff.parser.changecompare import ChangeCompare

class HtmlView(object):
    '''Renders the prettydiff.parser::Parser diffs into HTML markup targeted
    for modern browsers.'''

    # buffer used during render to append markup
    ui = []

    # reference to the current diff being rendered
    diff = None


    CHANGE_DELIMITERS = {
        'left': '<span style="background: #bfbfdc;">',
        'right': '</span>',
        'insert': '<span style="border:1px solid #bfbfdc; border-top:none; border-bottom:none; padding:2px 1px 2px 0; width:1px; margin:0 -2px 0 -1px;"></span>'
    }

    # markup template
    HTML_PAGE_HEAD = '''<!DOCTYPE html>
<html>
<head>
  <title>%s</title>
</head>
<body>
  <style type="text/css">
    BODY,TD {
      font-size:10pt;
      font-family: consolas, courier;
      white-space:nowrap;
    }
    TABLE { border-collapse: collapse; border-spacing: 0px; }

    .normal { background-color: #FFF; }
    .added { background-color: #BFB; }
    .removed { background-color: #FCC; }
    .modified { background-color: #DDF; }

    TD.linenum {
       color: #909090;
       text-align: right;
       vertical-align: top;
       font-weight: bold;
       padding-right:3px;
    }
    .compare TD.added,
    .compare TD.removed,
    .compare TD.modified,
    .compare TD.normal {
       border-right: 1px solid #888;
       border-left: 1px solid #888;
       padding:0 3px;
    }
    .compare TD.top-edge { border-bottom:1px solid #888; XXheight:5px; }
    .compare TD.bottom-edge { border-top:1px solid #888; XXheight:5px; }
    .compare H3 { margin:10px 0 0; }

    .compare tr.first TD { padding-top:3px; }
    .compare tr.last TD { padding-bottom:3px; }

    I.pipe { font-style:normal; color:#ccc; }

    .changes {
        border-radius:3px;
        padding:2px;
        margin-bottom:1px;
    }

    .changes table { width:100%%; }

    .changes .label { font-weight:bold; padding-left:5px; }
    .changes .index { width:100%%; }

    .changes .index em { font-style:normal; padding:0 2px 0 4px; }
    .changes .index a { text-decoration:none; padding:0 4px; }
    .changes .index a:hover { text-decoration:underline; }

    H1.diff {
        font-size:18px;
        color:#fff;
        text-shadow: 0 1px 1px rgba(0, 0, 0, 0.75);
        padding:5px 8px;
        border-radius:3px;

        background-color: #777777;
        background-repeat: repeat-x;
        background-image: -khtml-gradient(linear, left top, left bottom, from(#aaaaaa), to(#777777));
        background-image: -moz-linear-gradient(top, #aaaaaa, #777777);
        background-image: -ms-linear-gradient(top, #aaaaaa, #777777);
        background-image: -webkit-gradient(linear, left top, left bottom, color-stop(0%%, #aaaaaa), color-stop(100%%, #777777));
        background-image: -webkit-linear-gradient(top, #aaaaaa, #777777);
        background-image: -o-linear-gradient(top, #aaaaaa, #777777);
        background-image: linear-gradient(top, #aaaaaa, #777777);
        /*
          enabling this IE filter loses the borde radius:
          filter: progid:DXImageTransform.Microsoft.gradient(startColorstr='#aaaaaa', endColorstr='#777777', GradientType=0);
        */
    }

    .snipped { border-top:1px dashed #000; border-bottom:1px dashed #000; }
    .snipped-spacer { font-size:3px; }


  </style>
'''
    EM = '<em>%s</em>'

    NBSP = '&nbsp;'

    HTML_ENTITY_MAP = {
        '&': '&amp;',
        '"': '&quot;',
        '>': '&gt;',
        '<': '&lt;',
        "'": '&apos;'
    }

    HTML_DIFF_HEADING = '''<h1 class="diff"><a name="%s">%s</a></h1>'''

    HTML_CHANGES_INDEX = '''
    <div class="changes added">
      <table>
        <tr><td class="label">&nbsp;&nbsp;&nbsp;Added&nbsp;-</td><td class="index">%s</td></tr>
      </table>
    </div>
    <div class="changes removed">
      <table>
        <tr><td class="label removed">&nbsp;Removed&nbsp;-</td><td class="index removed">%s</td></tr>
      </table>
    </div>
    <div class="changes modified">
      <table>
        <tr><td class="label">Modified&nbsp;-</td><td class="index">%s</td></tr>
      </table>
    </div>
    '''

    HTML_PAGE_LINK = '<a %s="%s">%s</a>'

    HTML_SIDE_BY_SIDE_HEAD = '''
<table class="compare">
    <tr>
        <td width="16">&nbsp;</td>
        <td width="50%%">
          <h3>Older rev: %s%s</h3>
          %d lines removed <i class="pipe">|</i>
          %d lines modified <i class="pipe">|</i>
          Last modified: %s
        </td>
        <td width="16">&nbsp;</td>
        <td width="16">&nbsp;</td>
        <td width="50%%">
          <h3>Newer rev: %s%s</h3>
          %d lines added <i class="pipe">|</i>
          %d lines modified <i class="pipe">|</i>
          Last modified: %s
        </td>
    </tr>

    <tr>
       <td></td>
       <td class="top-edge"></td>
       <td></td>
       <td></td>
       <td class="top-edge"></td>
    </tr>
    '''

    HTML_SIDE_BY_SIDE_BODY = '''
    <tr%s>
      <td class="linenum">%s</td>
      <td class="%s">%s</td>
      <td width="16">&nbsp;</td>
      <td class="linenum">%s</td>
      <td class="%s">%s</td>
    </tr>
    '''
    HTML_SIDE_BY_SIDE_BODY_SNIPPED_ROW = '''
    <tr>
      <td></td>
      <td class="snipped"></td>
      <td class="snipped-spacer">&nbsp;</td>
      <td></td>
      <td class="snipped"></td>
    </tr>
    '''
    HTML_SIDE_BY_SIDE_FOOT = '''
    <tr>
       <td></td>
       <td class="bottom-edge"></td>
       <td></td>
       <td></td>
       <td class="bottom-edge"></td>
    </tr>
  </table><br>
'''
    HTML_PAGE_FOOT = '\n  </body>\n</html>'

    def render(self, diffs):
        '''Renders the given array of calculated diffs into markup.'''
        self.ui.append(self.HTML_PAGE_HEAD % 'Side-by-Side HTML Diff')

        for self.diff in diffs:
            self._render_heading()
            self._render_changes_index()
            self._render_side_by_side()

        self.ui.append(self.HTML_PAGE_FOOT)

        return ''.join(self.ui)

    def _render_heading(self):
        '''Renders the diff's heading.'''
        self.ui.append(self.HTML_DIFF_HEADING % (self.diff.file, self.diff.file))

    def _render_changes_index(self):
        '''Renders a diff's change index table which summarizes the added,
        removed, and modified lines and provides links from the changed
        line(s) to the source below.'''

        # these lists will hold the start/end line # for the different changes
        groups = {
            prettydiff.ADDED: [],
            prettydiff.REMOVED: [],
            prettydiff.MODIFIED: []
        }

        # iterate the chunks in the diff and group adjacent changes together
        for chunk in self.diff.chunks:
            for change in chunk.A.lines: self._group_changes('a', groups, change)
            for change in chunk.B.lines: self._group_changes('b', groups, change)

        self.ui.append(
            self.HTML_CHANGES_INDEX % (self._change_links(groups[prettydiff.ADDED]),
                                       self._change_links(groups[prettydiff.REMOVED]),
                                       self._change_links(groups[prettydiff.MODIFIED])))

    def _group_changes(self, side, groups, change):
        '''Groups lines of adjacent changes to minimize the number of links
        rendered in the change index table.'''

        # skip null change placeholders or changes marked 'normal'
        if change is None or prettydiff.NORMAL == change.status:
            return

        # figure out which changes list to use (see _render_changes_index)
        changes = groups[change.status]

        line_num = change.line_num
        last_index = len(changes) - 1
        prev = None if last_index < 0 else changes[last_index]

        # if at least one change has been made, and if the last change occurred
        # on the line number immediately preceding the current line number,
        # then group this change with the last change:
        #     (1, 2, 3, 22, 40, 41) ==> (1-3, 22, 40-41)
        if prev and side == prev['side'] and line_num == 1+prev['end']:
            prev['end'] = line_num
        else:
            changes.append({
                'start': line_num,
                'end':  line_num,
                'side': side
            })

    def _change_links(self, group):
        '''Converts the changes for the given group into clickable links.'''

        # if the passed group is empty, return a simple label
        if not group: return self.EM%'None'

        (prev_side, html) = (False, [])

        for ch in group:
            (side, start, end) = (ch['side'], str(ch['start']), str(ch['end']))
            label = start if start==end else start + '-' + end

            # add a label on the first pass
            if not html:
                html.append(self.EM%'Older' if side=='a' else self.EM%'Newer')
                prev_side = side if side=='a' else False
            # add a label if the side changes from the previous
            elif prev_side and prev_side != side:
                html.append(self.NBSP + self.EM%'Newer')
                prev_side = False

            html.append(self._anchor(side, start, label))

        return ''.join(html)

    def _anchor(self, side, line_num, label = None):
        '''Generates a named or linked anchor to a line of code.'''

        # unique id is built from the file name, side (a or b) and line number
        id = "%s_%s_%s" % (self.diff.file, side, str(line_num))

        # if ... generate named anchor: <a name="rev1_rev2_99">99</a>
        # else ... generate linked anchor: <a href="#rev1_rev2_99">99..103</a>
        if label is None:
            label = str(line_num)
            attr = 'name'
        else:
            attr = 'href'
            id = '#' + id

        return self.HTML_PAGE_LINK % (attr, id, label)

    def _render_side_by_side(self):
        '''Generates the html markup for the side-by-side diff.'''
        (html, ui, diff) = ([], self.ui, self.diff)

        noteA = ' (file created)' if not diff.existsA else ''
        noteB = ' (file deleted)' if not diff.existsB else ''

        # lines removed A, lines modified A, lines added B, lines modified B
        (removed, modifiedA, added, modifiedB) = (0, 0, 0, 0)

        for (chunkIndex, chunk) in enumerate(diff.chunks):
            count = len(chunk.A.lines) # A and B are the same length

            # add the appearance of a "clipped" row between subsequent chunks
            if (chunkIndex > 0): html.append(self.HTML_SIDE_BY_SIDE_BODY_SNIPPED_ROW)

            for (i, a, b) in izip(range(count), chunk.A.lines, chunk.B.lines):

                if a is None:
                    (dataA, statA, lineA) = (self.NBSP, prettydiff.ADDED, self.NBSP)
                else:
                    dataA = self._esc(a.data)
                    statA = a.status
                    lineA = self._anchor('a', a.line_num)
                    # tally lines removed/modified
                    if statA == prettydiff.REMOVED:
                        removed += 1
                    elif statA == prettydiff.MODIFIED:
                        modifiedA += 1

                if b is None:
                    (dataB, statB, lineB) = (self.NBSP, prettydiff.REMOVED, self.NBSP)
                else:
                    dataB = self._esc(b.data)
                    statB = b.status
                    lineB = self._anchor('b', b.line_num)
                    # tally lines added/modified
                    if statB == prettydiff.ADDED:
                        added += 1
                    elif statB == prettydiff.MODIFIED:
                        modifiedB += 1

                if statA == prettydiff.MODIFIED:
                    # mark up the differences between a and b; it is very
                    # important that the original (non-encoded) strings be
                    # passed to mark_change otherwise entities get mangled
                    (dataA, dataB) = ChangeCompare.mark_change(a.data, b.data)
                    dataA = ChangeCompare.swap_markers(self._esc(dataA), self.CHANGE_DELIMITERS)
                    dataB = ChangeCompare.swap_markers(self._esc(dataB), self.CHANGE_DELIMITERS)

                if i==0: edge_row_class = ' class="first"'
                elif i==count-1: edge_row_class = ' class="last"'
                else: edge_row_class = ''

                html.append(self.HTML_SIDE_BY_SIDE_BODY % (edge_row_class,
                                                           lineA, statA, dataA, lineB, statB, dataB))
        ui.append(self.HTML_SIDE_BY_SIDE_HEAD %
                  (diff.revA, noteA, removed, modifiedA, diff.timestampA,
                   diff.revB, noteB, added,   modifiedB, diff.timestampB))

        ui.append(''.join(html))
        ui.append(self.HTML_SIDE_BY_SIDE_FOOT)

    @staticmethod
    def _esc(html):
        '''Converts the entity chars in the given html using a pre-configured
        entity map. Also strips trailing \\n and converts spaces to &nbsp;.'''

        # convert all entity characters
        html = ''.join(HtmlView.HTML_ENTITY_MAP.get(c,c) for c in html)

        # strip trailing \n and convert spaces to non-breaking space
        return html.rstrip('\n').replace(' ', HtmlView.NBSP)
