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

import urllib2
import re
import os.path
from lxml import etree

class XsdParser:
    def __init__(self):
        self.cwd = os.path.dirname(os.path.realpath(__file__))
        self.xccdfXsdPath = '/usr/share/openscap/schemas/xccdf/1.2/'
        self.ovalXsdPath = '/usr/share/openscap/schemas/oval/5.10.1/'

    def setXsd(self, url):
        knownXsds = {'http://scap.nist.gov/schema/xccdf/1.2/xccdf_1.2.xsd' : 'xccdf_1.2.xsd',
            'http://oval.mitre.org/XMLSchema/oval-definitions-5' : 'oval-definitions-schema.xsd',
            'http://oval.mitre.org/XMLSchema/oval-common-5' : 'oval-common-schema.xsd',
            'http://oval.mitre.org/XMLSchema/oval-definitions-5#independent' : 'independent-definitions-schema.xsd',
            'http://oval.mitre.org/XMLSchema/oval-definitions-5#unix' : 'unix-definitions-schema.xsd',
            'http://oval.mitre.org/XMLSchema/oval-definitions-5#linux' : 'linux-definitions-schema.xsd'}
        self.children = {}
        self.attributes = {}

        self.__typeToName = {} # element type to name maping

        if (url in knownXsds.keys()):
            if (url.find('xccdf') > 0):
                path = self.xccdfXsdPath + knownXsds[url]
            else:
                path = self.ovalXsdPath + knownXsds[url]
            f = open(path, 'r')
            self.xsd = f.read()
            f.close()
        else:
            response = urllib2.urlopen(url)
            self.xsd = response.read()

        self.root = etree.fromstring(self.xsd)

    def parseChildren(self):
        # recursively for the tree
        for elem in self.root.iter():
            if elem.tag is etree.Comment:
                continue
            # interested only in element tags
            r = re.compile('.*element$')
            if r.match(elem.tag) is None:
                continue

            childName = elem.get('name')
            # reference instead of name?
            if childName is None:
                childName = elem.get('ref').split(':')[-1]
            # remember name to type maping
            elif elem.get('type') is not None:
                self.__typeToName[elem.get('type').split(':')[-1]] = childName

            parent = elem.getparent()
            while parent is not None and parent.tag.find('element') < 0:
                if parent.get('name') is not None:
                    break
                parent = parent.getparent()

            # get help for element
            helpText = "No help for this element available."
            doc = elem.find('{' + self.root.nsmap['xsd'] + '}annotation/' \
                    '{' + self.root.nsmap['xsd'] + '}documentation')
            if (doc is not None and doc.text is not None):
                helpText = " ".join(doc.text.split()) # get rid of awful original xml formatting

            # toplevel element
            if parent is None:
                self.__addItem(self.children, "<", {"hint" : childName, "help" : helpText})
                continue

            self.__addItem(self.children, "<" + parent.get('name') + "><", {"hint" : childName,
                "help" : helpText})

        # resolve types to names
        for type in self.__typeToName.keys():
            key = "<" + type + "><"
            if not key in self.children.keys():
                continue
            self.children["<" + self.__typeToName[type] + "><"] = self.children[key]
            self.__delItemFromRootChildren(self.children[key])
            del self.children[key]

    def parseAttributes(self):
        # recursively for the tree
        for elem in self.root.iter():
            if elem.tag is etree.Comment:
                continue
            # interested only in element tags
            r = re.compile('.*attribute$')
            if r.match(elem.tag) is None:
                continue

            attrName = elem.get('name')
            if attrName is None: # <xsd:attribute ref="xml:lang"/>
                continue

            # oval linux definitions workaround
            if (attrName == 'datatype'):
                continue

            parent = elem.getparent()
            while parent is not None and parent.tag.find('element') < 0:
                if parent.get('name') is not None:
                    break
                parent = parent.getparent()

            # get help for attribute
            helpText = "No help for this attribute available."
            doc = elem.find('{' + self.root.nsmap['xsd'] + '}annotation/' \
                    '{' + self.root.nsmap['xsd'] + '}documentation')
            if doc is not None:
                helpText = " ".join(doc.text.split()) # get rid of awful original xml formatting

            self.__addItem(self.attributes, "<" + parent.get('name') + " ", {"hint" : attrName 
                + '="', "help" : helpText})

        # resolve types to names
        for type in self.__typeToName.keys():
            key = "<" + type + " "
            if not key in self.attributes.keys():
                continue
            self.attributes["<" + self.__typeToName[type] + " "] = self.attributes[key]
            del self.attributes[key]

    def parse(self):
        self.parseChildren() # we need this to fill __typeToName mapping
        self.parseAttributes()
        self.hints = dict(self.children.items() + self.attributes.items())


    def __addItem(self, where, key, val):
        if not key in where.keys():
            where[key] = []
        where[key].append(val)

    def __delItemFromRootChildren(self, what):
        for itemToDel in what:
            for item in self.children['<']:
                if (item['hint'] == itemToDel['hint']):
                    self.children['<'].remove(item)

