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

import xsdparser

class OvalParser():
    def __init__(self):
        pass

        self.parsers = {'' : xsdparser.XsdParser(),
            'oval' : xsdparser.XsdParser(),
            'ind' : xsdparser.XsdParser(),
            'unix' : xsdparser.XsdParser(),
            'linux' : xsdparser.XsdParser()}

        self.parsers[''].setXsd('http://oval.mitre.org/XMLSchema/oval-definitions-5')
        self.parsers['oval'].setXsd('http://oval.mitre.org/XMLSchema/oval-common-5')
        self.parsers['ind'].setXsd('http://oval.mitre.org/XMLSchema/oval-definitions-5#independent')
        self.parsers['unix'].setXsd('http://oval.mitre.org/XMLSchema/oval-definitions-5#unix')
        self.parsers['linux'].setXsd('http://oval.mitre.org/XMLSchema/oval-definitions-5#linux')

        for parser in self.parsers.values():
            parser.parse()

        self.__setNspaces()

    def __setNspaces(self):
        self.children = self.parsers[''].children
        for nspace in sorted(self.parsers.keys())[1:]:
            for key in self.parsers[nspace].children.keys():
                if (key != '<'):
                    self.children[key[:1] + nspace + ':' + key[1:]] = []
                for hint in self.parsers[nspace].children[key]:
                    modifiedHint = hint
                    modifiedHint['hint'] = nspace + ':' + hint['hint']
                    if (key == '<'):
                        self.children['<'].append(modifiedHint)
                    else:
                        self.children[key[:1] + nspace + ':' + key[1:]].append(modifiedHint)

        self.attributes = self.parsers[''].attributes
        for nspace in sorted(self.parsers.keys())[1:]:
            for key in self.parsers[nspace].attributes.keys():
                self.attributes[key[:1] + nspace + ':' + key[1:]] = []
                for hint in self.parsers[nspace].attributes[key]:
                    modifiedHint = hint
                    modifiedHint['hint'] = nspace + ':' + hint['hint']
                    self.attributes[key[:1] + nspace + ':' + key[1:]].append(modifiedHint)

        self.hints = dict(self.children.items() + self.attributes.items())
        
