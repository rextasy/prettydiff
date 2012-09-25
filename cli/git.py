import re
import subprocess

class Git(object):
    '''Handles the shell parsing of git revisions to generate a unified diff.'''

    @staticmethod
    def emailToHtml(addr):
        addr = addr.strip()
        m = re.match('([^<]+) <([^>]+)>', addr)
        name = m.group(1)
        email = m.group(2)
        return '%s &lt;<a href="mailto:%s">%s</a>&gt;' % (name, addr, email)

    def getUnifiedDiff(self, cli):
        # add any additional processing to the given command line interface
        args = cli.parse_args()
        filename = args.filename

        # query the
        pipe = subprocess.Popen(["git", "log", "-n", "2", filename], shell=True, stdout=subprocess.PIPE)

        # parse the stdout from the above command to find each changeset revision id

        revNew = pipe.stdout.readline()
        revNewInfo = Git.emailToHtml(pipe.stdout.readline()[8:])
        revNewInfo = pipe.stdout.readline()[8:] + ' -- ' + revNewInfo

        while True:
            revOld = pipe.stdout.readline()
            if 0 == revOld.find("commit"):
                revOldInfo = Git.emailToHtml(pipe.stdout.readline()[8:])
                revOldInfo = pipe.stdout.readline()[8:] + ' -- ' + revOldInfo
                break

        (_, revNew) = re.split(' +', revNew.strip())
        (_, revOld) = re.split(' +', revOld.strip())

        pipe = subprocess.Popen(["git", "diff", "-U100", revOld, revNew, filename],
            shell=True, stdout=subprocess.PIPE)

        diff = pipe.stdout.readlines()

        # convert git unified diff headers into hg diff headers
        # TODO: need to rethink this

        diff[0] = 'diff -r %s -r %s %s\n' % (revOld, revNew, filename)
        diff[2] = diff[2].replace('\n', '\t%s\n' % revOldInfo)
        diff[3] = diff[3].replace('\n', '\t%s\n' % revNewInfo)

        return diff
