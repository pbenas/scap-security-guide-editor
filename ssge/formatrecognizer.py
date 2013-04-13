#!/usr/bin/env python

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

