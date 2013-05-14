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

import re

from lxml import etree

class OvalIds:
    def __init__(self):
        pass

    def getIdsFromFile(self, filename):
        f = open(filename)
        text = f.read()
        f.close()

        # remove all namespaces. lxml can't work with unknown namespaces and namespaces are irrelevant
        # for this case

        nspaceStartRemover = re.compile('<\w+:')
        nspaceEndRemover = re.compile('<\/\w+:')
        nspaceAttributeRemover = re.compile(' \w+:')

        text = nspaceStartRemover.sub('<',text)
        text = nspaceEndRemover.sub('</',text)
        text = nspaceAttributeRemover.sub(' ',text)

        root = etree.fromstring(text)
        for elem in root.iter():
            if elem.tag is etree.Comment:
                continue
            # interested only in description tags
            if elem.tag.find('description') < 0:
                continue

            description = elem.text
           
            # parent of description should me <metadata> which parent should be <definition> 
            # carrying the "id" attribute
            id = elem.getparent().getparent().get('id')

            return (id, description)

