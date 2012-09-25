# Copyright (C) 2012 Rex Staples
# Contact: rstaples@gmail.com

"""A diff pretty printer."""

__version__ = '1.0'
__author__ = 'Rex Staples <rstaples@gmail.com>'

__all__ = [
    'convert'
    'ADDED',
    'NORMAL',
    'REMOVED',
    'MODIFIED'
]

# line diff statuses
ADDED = 'added'
NORMAL = 'normal'
REMOVED = 'removed'
MODIFIED = 'modified'

def convert(diff_lines, view = 'email'):

    if view == 'email':
        from .view.emailview import EmailView
        ui = EmailView()
    else:
        from .view.htmlview import HtmlView
        ui = HtmlView()

    from .parser.diffparser import DiffParser
    return ui.render(DiffParser(diff_lines).diffs)
