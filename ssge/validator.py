# Copyright (c) 2013 Petr Benas <pbenas@redhat.com>
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

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

