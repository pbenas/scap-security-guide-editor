#!/usr/bin/env python

import subprocess
import tempfile
import os

class Validator:
    def __init__(self):
        pass

    def validateUserFile(self, text, type):
        fd = tempfile.mkstemp()
        (f, name) = fd
        os.write(f, text)

        process = subprocess.Popen(['oscap', type, 'validate', name], stdout = subprocess.PIPE, \
                stderr = subprocess.PIPE)
        (stdout, stderr) = process.communicate()

        os.close(f)

        if (process.returncode == 0 and stderr == "" and stdout == ""):
            return 'Your ' + type + ' file is valid'

        output = ''
        if (stderr != ""):
            # remove temporary filename like "/tmp/tmprWd1w4:"
            output += ':'.join(stderr.split(':')[1:])

        if (stdout != ""):
            # remove temporary filename like "File '/tmp/tmp0nvTLa' "
            output += ' '.join(stdout.split()[2:])

        if output:
            return output
        else:
            return 'oscap return code was ' + str(process.returncode) + ', stdout: ' + \
                    stdout + ', stderr: ' + stderr

