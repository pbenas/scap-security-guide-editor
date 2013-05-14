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

from lxml import etree

class FormatRecognizer:
    def __init__self():
        pass

    def recognize(self, text):
        if (text == ""):
            return
        root = etree.fromstring(text)
        xccdf = oval = False
        for nspace in  root.nsmap.values():
            if (nspace.find('oval') > 0):
                oval = True
            if (nspace.find('xccdf') > 0):
                xccdf = True

        if (oval and not xccdf):
            return 'oval'
        else:
            return 'xccdf'

    def getMainNspace(self, text):
        root = etree.fromstring(text)
        return root.nsmap[None]

