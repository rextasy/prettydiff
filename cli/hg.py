import re
import subprocess

class Hg(object):
    '''Handles the shell parsing of mercurial revisions to generate a unified diff.'''

    def getUnifiedDiff(self, cli):
        # add any additional processing to the given command line interface
        args = cli.parse_args()
        filename = args.filename

        # query the
        pipe = subprocess.Popen(["hg", "log", "-l", "2", filename], shell=True, stdout=subprocess.PIPE)

        # parse the stdout from the above command to find each changeset revision id

        revNew = pipe.stdout.readline()
        while True:
            revOld = pipe.stdout.readline()
            if 0 == revOld.find("changeset:"): break

        (_, revNew) = re.split(' +', revNew.strip())
        (_, revOld) = re.split(' +', revOld.strip())

        pipe = subprocess.Popen(["hg", "diff", "-U", "100", "-r", revOld, "-r", revNew, filename],
            shell=True, stdout=subprocess.PIPE)

        return pipe.stdout.readlines()
