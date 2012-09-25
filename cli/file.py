class File(object):
    '''Reads in a unified diff file from disk for use in the command-line interface.'''

    def getUnifiedDiff(self, cli):
        args = cli.parse_args()
        with open(args.filename) as f:
            difflines = f.readlines()
        f.close()
        return difflines