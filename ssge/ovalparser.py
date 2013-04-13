#!/usr/bin/env python

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
        
