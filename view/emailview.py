from itertools import izip
from prettydiff.parser.changecompare import ChangeCompare
import re, prettydiff

class EmailView(object):
    '''Renders the prettydiff.parser::Parser diffs into HTML markup suitable
    for emailing.'''

    # buffer used during render to append markup
    ui = []

    # reference to the current diff being rendered
    diff = None

    CHANGE_DELIMITERS = {
        'left': '<span style="background: #bfbfdc;">',
        'right': '</span>',
        #'insert': '<span style="border:1px solid #bfbfdc; border-top:none; border-bottom:none; padding:2px 1px 2px 0; width:1px; margin:0 -2px 0 -1px;color:pink;bgcolor:#ccf;">|</span>'
        'insert': '<span style="font-family:narrow,arial; border:1px solid #bfbfdc; color:#ddf;">|</span>'
    }
#<!--[if gte mso 9]>
#// This CSS will only be seen in Outlook 2007
#<![endif]-->
    CSS = {
        'tag': {
        },
        'class': {
            'heading': 'padding:5px;border-bottom:15px solid #fff;width:100%;background:#777;',
            'heading-tbody': 'border-collapse:collapse;', # this is for outlook to remove double bottom border
            'filename': 'font-weight:bold;font-family:consolas,courier;font-size:18px;color:#fff',
            'linenum': 'color:#909090;text-align:right;font-weight:bold;padding-right:3px;',
            'normal': 'background-color:#FFF;',
            'added':  'background-color:#BFB;',
            'removed':'background-color:#FCC;',
            'modified':'background-color:#DDF;',
            'compare': 'border-collapse:collapse; border-spacing:0px;',
            'side' : 'border-right:1px solid #888;border-left:1px solid #888;padding:0 3px;',
            'col': 'font-size:10pt;font-family:consolas,courier;white-space:nowrap;',
            'top-edge':'border-bottom:1px solid #888;',
            'bottom-edge': 'border-top:1px solid #888;',
            'first': 'padding-top:5px;vertical-align:bottom;',
            'last': 'padding-bottom:5px;vertical-align:top;',
            'pipe': 'font-style:normal; color:#ccc;',
            'changes': 'border-bottom:1px solid #fff;padding:2px;',
            'label': 'font-size:10pt;font-family:consolas,courier;white-space:nowrap;font-weight:bold; padding-left:5px;',
            'index': 'font-size:10pt;font-family:consolas,courier;white-space:nowrap;width:100%;',
            'change-label':'font-style:normal; margin:0 2px 0 4px;',
            'change-link': 'text-decoration:none;',
            'change-index': 'width:100%;',
            'snipped': 'border-top:1px dashed #888;border-bottom:1px dashed #888;',
            'snipped-spacer': 'font-size:3px;'
        }
    }
    
    # markup template
    HTML_PAGE_HEAD = '''


    '''

    EM = '<em style-class="change-label">%s</em>'

    NBSP = '&nbsp;'

    HTML_ENTITY_MAP = {
        '&': '&amp;',
        '"': '&#34;',
        '>': '&gt;',
        '<': '&lt;',
        "'": '&#39;'
    }

    HTML_DIFF_HEADING = '''<table style-class="heading" cellpadding="0" cellspacing="0" border="0">
    <tbody style-class="heading-tbody"><tr><td style-class="filename">%s</td></tr></tbody></table>'''

    HTML_CHANGES_INDEX = '''
    <table style-class="changes added change-index">
      <tr><td style-class="label">&nbsp;&nbsp;&nbsp;Added&nbsp;-</td><td style-class="index">%s</td></tr>
    </table>

    <table style-class="changes removed change-index">
      <tr><td style-class="label removed">&nbsp;Removed&nbsp;-</td><td style-class="index removed">%s</td></tr>
    </table>

    <table style-class="changes modified change-index">
      <tr><td style-class="label">Modified&nbsp;-</td><td style-class="index">%s</td></tr>
    </table>
    '''

    HTML_PAGE_LINK = '&nbsp;<a style-class="change-link" %s="%s">%s</a>&nbsp;'

    HTML_SIDE_BY_SIDE_HEAD = '''
<table style-class="compare">
    <tr>
        <td style-class="col">&nbsp;</td>
        <td style-class="col" width="50%%">
          <h3 style="margin:10px 0 0;">Older rev: %s%s</h3>
          %d lines removed <i style-class="pipe">|</i>
          %d lines modified <i style-class="pipe">|</i>
          Last modified: %s
        </td>
        <td style-class="col" width="16">&nbsp;</td>
        <td style-class="col">&nbsp;</td>
        <td style-class="col" width="50%%">
          <h3 style="margin:10px 0 0;">Newer rev: %s%s</h3>
          %d lines added <i style-class="pipe">|</i>
          %d lines modified <i style-class="pipe">|</i>
          Last modified: %s
        </td>
    </tr>

    <tr>
       <td></td>
       <td style-class="top-edge"></td>
       <td></td>
       <td></td>
       <td style-class="top-edge"></td>
    </tr>
    '''

    HTML_SIDE_BY_SIDE_BODY_FIRST_ROW = '''
    <tr>
      <td style-class="col first linenum" nowrap>%s</td>
      <td style-class="col first side %s">%s</td>
      <td style-class="col first" width="16">&nbsp;</td>
      <td style-class="col first linenum" nowrap>%s</td>
      <td style-class="col first side %s">%s</td>
    </tr>
    '''

    HTML_SIDE_BY_SIDE_BODY_MIDDLE_ROW = '''
    <tr>
      <td style-class="col linenum" nowrap>%s</td>
      <td style-class="col side %s">%s</td>
      <td style-class="col " width="16">&nbsp;</td>
      <td style-class="col linenum" nowrap>%s</td>
      <td style-class="col side %s">%s</td>
    </tr>
    '''

    HTML_SIDE_BY_SIDE_BODY_LAST_ROW = '''
    <tr>
      <td style-class="col last linenum" nowrap>%s</td>
      <td style-class="col last side %s">%s</td>
      <td style-class="col last" width="16">&nbsp;</td>
      <td style-class="col last linenum" nowrap>%s</td>
      <td style-class="col last side %s">%s</td>
    </tr>
    '''

    HTML_SIDE_BY_SIDE_BODY_SNIPPED_ROW = '''
    <tr>
      <td></td>
      <td style-class="snipped"></td>
      <td style-class="snipped-spacer">&nbsp;</td>
      <td></td>
      <td style-class="snipped"></td>
    </tr>
    '''

    HTML_SIDE_BY_SIDE_FOOT = '''
    <tr>
       <td></td>
       <td style-class="bottom-edge"></td>
       <td></td>
       <td></td>
       <td style-class="bottom-edge"></td>
    </tr>
  </table><br>
'''
    HTML_PAGE_FOOT = '\n'

    REGEX_TAG_STYLE_CLASS = '(?i)<(\w+) +style-class="([^"]*)"'

    def render(self, diffs):
        '''Renders the given array of calculated diffs into markup.'''
        self.ui.append(self.HTML_PAGE_HEAD)

        for self.diff in diffs:
            self._render_heading()
            self._render_changes_index()
            self._render_side_by_side()

        self.ui.append(self.HTML_PAGE_FOOT)

        html = ''.join(self.ui)
        return re.sub(self.REGEX_TAG_STYLE_CLASS, self._replaceStyle, html)

    def _replaceStyle(self, m):
        '''Given a MatchObject containing an html tag (group 1) and possibly a
        list of class names (group 2) this function looks up any style for the
        tag and each class name and returns a string in the form of:
        <tag style="<rules for class1> ... <rules for classN>'''

        tag = m.group(1) or ''
        css = self.CSS['tag'].get(tag.lower(), '')
        classNames = m.group(2) or ''

        for cls in re.split(' +', classNames):
            css += self.CSS['class'].get(cls, '')

        if css: css = ' style="%s"' % css.replace('\n', '')

        return '<' + tag + css

    def _render_heading(self):
        '''Renders the diff's heading.'''
        self.ui.append(self.HTML_DIFF_HEADING % self.diff.file)

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

                if i==0: row_template = self.HTML_SIDE_BY_SIDE_BODY_FIRST_ROW
                elif i==count-1: row_template = self.HTML_SIDE_BY_SIDE_BODY_LAST_ROW
                else: row_template = self.HTML_SIDE_BY_SIDE_BODY_MIDDLE_ROW

                html.append(row_template % (lineA, statA, dataA, lineB, statB, dataB))



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
        html = ''.join(EmailView.HTML_ENTITY_MAP.get(c,c) for c in html)

        # strip trailing \n and convert spaces to non-breaking space
        return html.rstrip('\n').replace(' ', EmailView.NBSP)
