# Copyright (C) 2012 Rex Staples
# Contact: rstaples@gmail.com

"""This is the command-line interface to the diff pretty printer."""

import sys, argparse, subprocess, tempfile, prettydiff
from prettydiff.cli.hg import Hg
from prettydiff.cli.git import Git
from prettydiff.cli.file import File

commandLine = argparse.ArgumentParser(
    description='Convert a unified diff into a side-by-side HTML diff.')

commandLine.add_argument('source', choices=['hg', 'git', 'file'],
    help='Specifies version control system to be used to generate the unified diff.' \
         'Use /file/ if the unified diff has already been generated into a file.' )

commandLine.add_argument('filename',
    help='The name of the resource to compare.')

commandLine.add_argument('--stdout',
    help='Output the resulting markup to the console.',
    action='store_true')

args = commandLine.parse_args()

try:
    SourceClass = {
        'hg': Hg,
        'git': Git,
        'file': File
    }[args.source]
except (IndexError, KeyError):
    # if something error'd then rely on the ArgumentParser to show instructions
    commandLine.parse_args()

# the getUnifiedDiff() method must return a unified diff as an array of lines

diff = SourceClass().getUnifiedDiff(commandLine)
html = prettydiff.convert(diff, 'html')

if(args.stdout):
    print html
else:
    # write the markup to a tempfile to be opened by the default system handler

    f = tempfile.NamedTemporaryFile(suffix='.html', delete=False)
    f.write(html)
    f.close()

    subprocess.call(f.name, shell=True)
